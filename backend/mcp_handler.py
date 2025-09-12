import os
import re 
import json
import logging
import inspect  
from typing import Optional, Any, Dict, Union
from datetime import datetime, timezone

# LiveKit imports
from livekit.agents.llm import function_tool

# MCP imports
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from .config import Config

# Global MCP client to persist across tool calls
mcp_client = None
mcp_tools_cache = None

async def initialize_mcp_client():
    """Initialize the MCP client globally and return tools with server names."""
    global mcp_client
    
    if not Config.COMPOSIO_MCP_URL:
        raise ValueError("COMPOSIO_MCP_URL environment variable is required")
    
    logging.info(f"🔗 Connecting to MCP servers: {Config.COMPOSIO_MCP_URL}, {Config.N8N_MCP_SERVER_URL}")
    
    mcp_client = MultiServerMCPClient({
        "composio": {"url": Config.COMPOSIO_MCP_URL, "transport": "streamable_http"},
       # "n8n-self-hosted": {"url": Config.N8N_MCP_SERVER_URL, "transport": "streamable_http"},
    })
    
    all_tools_with_servers = []
    
    try:
        async with mcp_client.session("composio") as session:
            composio_tools = await load_mcp_tools(session)
            for tool in composio_tools:
                all_tools_with_servers.append((tool, "composio"))
            logging.info(f"✅ Composio MCP: {len(composio_tools)} tools loaded")
        
 #       if Config.N8N_MCP_SERVER_URL:
 #           async with mcp_client.session("n8n-self-hosted") as session:
  #              n8n_tools = await load_mcp_tools(session)
  #              for tool in n8n_tools:
   #                 all_tools_with_servers.append((tool, "n8n-self-hosted"))
    #            logging.info(f"✅ n8n MCP: {len(n8n_tools)} tools loaded")
        
        return all_tools_with_servers
    
    except Exception as e:
        logging.error(f"❌ MCP connection failed: {e}", exc_info=True)
        raise


def create_mcp_tool_wrapper(mcp_tool, tool_index: int, server_name: str):
    """Create a robust, LiveKit-ready wrapper for an MCP tool with parameter remapping."""

    safe_name = (
        mcp_tool.name.replace("-", "_")
                       .replace(" ", "_")
                       .replace(".", "_")
                       .replace("/", "_")
                       .lower()
    )
    tool_name = f"{safe_name}_{tool_index}"
    description = mcp_tool.description or f"Execute {mcp_tool.name}"
    original_tool_name = mcp_tool.name

    # 1. Discover parameters for the function signature
    parameters = []
    tool_schema = getattr(mcp_tool, 'args_schema', None)
    
    if tool_schema and hasattr(tool_schema, '__fields__'):
        for field_name, field_info in tool_schema.__fields__.items():
            param_type = str
            if hasattr(field_info, 'annotation'):
                if field_info.annotation == int: param_type = int
                elif field_info.annotation == bool: param_type = bool
                elif field_info.annotation == float: param_type = float
            parameters.append((field_name, param_type))
    else:
        # Smarter fallback based on tool name
        tool_name_lower = original_tool_name.lower()
        if 'search' in tool_name_lower or 'crawl' in tool_name_lower:
            parameters = [("query", str)]
        elif 'send' in tool_name_lower and ('gmail' in tool_name_lower or 'email' in tool_name_lower):
            parameters = [("to", str), ("subject", str), ("body", str)]
        elif 'create_event' in tool_name_lower and 'calendar' in tool_name_lower:
             parameters = [("summary", str), ("start_time", str), ("end_time", str)]
        elif 'update_event' in tool_name_lower and 'calendar' in tool_name_lower:
             parameters = [("id", str), ("summary", str), ("start_time", str), ("end_time", str)]
        elif 'delete_event' in tool_name_lower and 'calendar' in tool_name_lower:
             parameters = [("id", str)]
        else:
            parameters = [("input", str)]

    # 2. Define the core logic of the function
    async def wrapper(**kwargs) -> str:
        global mcp_client
        logging.info(f"[{tool_name}] called on server: {server_name} with args: {kwargs}")

        if not mcp_client: return "Error: MCP client not initialized"

        try:
            filtered_args = {k: v for k, v in kwargs.items() if v is not None}
            
            # Pre-convert datetimes to UTC
            tool_name_lower_check = original_tool_name.lower()
            if 'calendar' in tool_name_lower_check:
                for key in ['start_time', 'end_time']:
                    if key in filtered_args and isinstance(filtered_args[key], str):
                        try:
                            dt_obj = datetime.fromisoformat(filtered_args[key])
                            utc_dt_str = dt_obj.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                            filtered_args[key] = utc_dt_str
                            logging.info(f"[{tool_name}] Converted '{key}' to UTC: {utc_dt_str}")
                        except ValueError:
                            logging.warning(f"[{tool_name}] Could not parse datetime string for '{key}': {filtered_args[key]}")

            # Argument Remapping Logic
            remapped_args = filtered_args.copy()
            if ('search' in tool_name_lower_check or 'crawl' in tool_name_lower_check) and 'input' in remapped_args and 'query' not in remapped_args:
                remapped_args['query'] = remapped_args.pop('input')
                logging.info(f"[{tool_name}] Remapped 'input' -> 'query'")

            if 'calendar' in tool_name_lower_check:
                if 'start_time' in remapped_args and 'start_datetime' not in remapped_args:
                    remapped_args['start_datetime'] = remapped_args.pop('start_time')
                    logging.info(f"[{tool_name}] Remapped 'start_time' -> 'start_datetime'")
                if 'end_time' in remapped_args and 'end_datetime' not in remapped_args:
                    remapped_args['end_datetime'] = remapped_args.pop('end_time')
                    logging.info(f"[{tool_name}] Remapped 'end_time' -> 'end_datetime'")
                if ('update_event' in tool_name_lower_check or 'delete_event' in tool_name_lower_check) and 'id' in remapped_args and 'event_id' not in remapped_args:
                    remapped_args['event_id'] = remapped_args.pop('id')
                    logging.info(f"[{tool_name}] Remapped 'id' -> 'event_id'")
            
            if 'send' in tool_name_lower_check and 'gmail' in tool_name_lower_check and 'to' in remapped_args and 'recipient_email' not in remapped_args:
                remapped_args['recipient_email'] = remapped_args.pop('to')
                logging.info(f"[{tool_name}] Remapped 'to' -> 'recipient_email'")


            final_args = remapped_args
   #         if server_name == "n8n-self-hosted":
     #           if not (len(final_args) == 1 and "input" in final_args):
      #              final_args = {"input": json.dumps(final_args)}
       #             logging.info(f"[{tool_name}] Repackaged args for n8n: {final_args}")
            
            async with mcp_client.session(server_name) as session:
                session_tools = await load_mcp_tools(session)
                current_tool = next((t for t in session_tools if t.name == original_tool_name), None)
                
                if not current_tool:
                    error_msg = f"Error: Tool '{original_tool_name}' not found on server '{server_name}'"
                    logging.error(f"[{tool_name}] {error_msg}")
                    return error_msg
                
                result = await current_tool.ainvoke(final_args)
                logging.info(f"[{tool_name}] Raw result: {result}")

                if isinstance(result, (dict, list, tuple)):
                    return json.dumps(result, indent=2)
                return str(result)

        except Exception as e:
            error_msg = f"MCP tool error: {str(e)}"
            logging.error(f"[{tool_name}] {error_msg}", exc_info=True)
            return error_msg

    # 3. Build the function signature and type hints for LiveKit
    sig_params = []
    annotations_dict = {}
    for param_name, param_type in parameters:
        optional_type = Optional[param_type]
        annotations_dict[param_name] = optional_type
        sig_params.append(
            inspect.Parameter(
                param_name,
                inspect.Parameter.KEYWORD_ONLY,
                default=None,
                annotation=optional_type
            )
        )
    annotations_dict['return'] = str

    # 4. Attach the metadata to the wrapper function
    wrapper.__name__ = tool_name
    wrapper.__doc__ = description
    wrapper.__annotations__ = annotations_dict
    wrapper.__signature__ = inspect.Signature(parameters=sig_params)
    
    return function_tool(wrapper)


async def load_and_convert_mcp_tools():
    """Load MCP tools and convert them to LiveKit function tools."""
    global mcp_client, mcp_tools_cache
    
    logging.info("🔄 Loading MCP tools from all servers...")
    
    try:
        all_mcp_tools_with_servers = await initialize_mcp_client()
        livekit_tools = []
        mcp_tools_cache = []
        
        for i, (mcp_tool, server_name) in enumerate(all_mcp_tools_with_servers):
            try:
                wrapper = create_mcp_tool_wrapper(mcp_tool, i, server_name)
                livekit_tools.append(wrapper)
                mcp_tools_cache.append(mcp_tool)
                logging.info(f"✅ Created wrapper for tool {i}: {mcp_tool.name} (from {server_name})")
            except Exception as tool_error:
                logging.error(f"❌ Failed to create wrapper for tool {mcp_tool.name}: {tool_error}", exc_info=True)
        
        logging.info(f"🎯 Successfully loaded {len(livekit_tools)} MCP tools")
        return livekit_tools
        
    except Exception as e:
        logging.error(f"❌ Failed to load MCP tools: {e}", exc_info=True)
        return []
