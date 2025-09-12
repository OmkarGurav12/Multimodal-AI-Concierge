import os
import json
import logging
from mem0 import AsyncMemoryClient
from livekit.agents import ChatContext

from .config import Config

async def load_memories():
    """1st Database Fetch - Load existing memories at conversation start"""
    if not Config.MEM0_API_KEY:
        logging.warning("⚠️ MEM0_API_KEY not found. Memory functionality will be limited.")
        return AsyncMemoryClient(), ChatContext(), '', Config.DEFAULT_USER
    
    try:
        mem0 = AsyncMemoryClient()
        user_name = Config.DEFAULT_USER
        
        # Use v1.1 format for consistency
        results = await mem0.get_all(user_id=user_name, output_format='v1.1')
        initial_ctx = ChatContext()
        memory_str = ''
        
        if results and results.get('results', []):
            memories = [
                {
                    "memory": result["memory"],
                    "updated_at": result["updated_at"]
                }
                for result in results.get('results', [])
            ]
            memory_str = json.dumps(memories)
            logging.info(f"🧠 Loaded memories: {memory_str}")
            initial_ctx.add_message(
                role="assistant",
                content=f"The user's name is {user_name}, and this is relevant context: {memory_str}."
            )
        else:
            logging.info("🧠 No existing memories found for user")
        
        return mem0, initial_ctx, memory_str, user_name
    
    except Exception as e:
        logging.error(f"❌ Error initializing Mem0 client: {e}")
        return AsyncMemoryClient(), ChatContext(), '', Config.DEFAULT_USER


async def shutdown_hook(chat_ctx: ChatContext, mem0: AsyncMemoryClient, memory_str: str, user_name: str):
    """2nd Database Save - Save memories at conversation end"""
    logging.info("🧠 Shutting down, saving chat context to memory...")
    messages_formatted = []
    
    logging.info(f"Chat context messages: {len(chat_ctx.items)} items")
    
    for i, item in enumerate(chat_ctx.items):
        try:
            # Extract role safely
            role = getattr(item, 'role', None)
            if role not in ['user', 'assistant']:
                continue
            
            # Extract content with multiple fallbacks
            content_str = ""
            for attr in ['content', 'text', 'message', 'text_content']:
                if hasattr(item, attr):
                    content = getattr(item, attr)
                    if content is not None:
                        if isinstance(content, list):
                            content_str = ''.join(str(c) for c in content)
                        else:
                            content_str = str(content)
                        break
            
            if not content_str.strip() or (memory_str and memory_str in content_str):
                continue
            
            messages_formatted.append({
                "role": role,
                "content": content_str.strip()
            })
            
        except Exception as e:
            logging.warning(f"Error processing chat item {i}: {e}")
            continue
    
    if messages_formatted:
        logging.info(f"💾 Attempting to save {len(messages_formatted)} messages to memory")
        try:
            # Use the newer v1.1 API format - explicitly specify output_format
            result = await mem0.add(
                messages_formatted, 
                user_id=user_name,
                output_format='v1.1'  # Add this line to fix the warning
            )
            logging.info(f"✅ Chat context saved to memory successfully: {result}")
        except Exception as e:
            logging.error(f"❌ Failed to save memories: {e}")
    else:
        logging.info("ℹ️ No valid messages found to save to memory")
