import json
import logging
import asyncio
from openai import AsyncOpenAI
import os
# LiveKit imports
from livekit.agents import AgentSession, cli, WorkerOptions, RoomInputOptions, JobContext , Agent, JobContext, ChatContext, llm
from livekit.plugins import deepgram, silero, groq, elevenlabs, noise_cancellation, cartesia, openai, tavus

# Local imports
from .config import Config, validate_environment
from .mcp_handler import load_and_convert_mcp_tools
from .memory_handler import load_memories, shutdown_hook
from .agent import MCPAssistant
from mem0 import AsyncMemoryClient
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def entrypoint(ctx: JobContext):
    logging.info("🚀 Starting MCP + LiveKit + Mem0 Voice Agent")

    # --- IMMEDIATE, FAST SETUP ---
    # Create the LiveKit session objects first. This is all local and very fast.
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="en"),
        llm=openai.LLM(
            model=Config.OPENROUTER_MODEL,
            client=AsyncOpenAI(
                api_key=Config.OPENROUTER_API_KEY,
                base_url=Config.OPENROUTER_BASE_URL,
                default_headers={
                    "HTTP-Referer": "livekit-agent",
                    "X-Title": "LiveKit Agent",
                }
            ),
            temperature=Config.LLM_TEMPERATURE,
            timeout=Config.LLM_TIMEOUT,
        ),
        tts=cartesia.TTS(voice=Config.CARTESIA_VOICE_ID, model=Config.CARTESIA_MODEL),
        vad=silero.VAD.load(),
    )

    avatar = tavus.AvatarSession(
        replica_id=Config.AVATAR_REPLICA_ID,
        persona_id=Config.AVATAR_PERSONA_ID
    )

    # --- 1. CONNECT IMMEDIATELY ---
    # Connect the avatar to the room right away. This satisfies the 10-second timer.
    logging.info("Connecting avatar to the room...")
    await avatar.start(session, room=ctx.room)
    logging.info("✅ Avatar connected.")

    # --- 2. NOW, PERFORM SLOW INITIALIZATIONS ---
    # Now that we are connected, we can safely load tools and memories.
    logging.info("Loading MCP tools and memories...")
    try:
        validate_environment()
        logging.info("🔄 Loading MCP tools...")
        mcp_tools = await load_and_convert_mcp_tools()
        if not mcp_tools:
            logging.warning("⚠️ No MCP tools loaded, agent will run without external tools")
        
        logging.info("🔄 Loading memories...")
        mem0, initial_ctx, memory_str, user_name = await load_memories()
        
        tool_count = len(mcp_tools)
        memory_count = len(json.loads(memory_str)) if memory_str else 0
        logging.info(f"✅ Loaded {tool_count} tools and {memory_count} memories.")

    except Exception as e:
        logging.error(f"❌ Failed during initialization: {e}", exc_info=True)
        mcp_tools = []
        mem0 = AsyncMemoryClient()
        initial_ctx = ChatContext()
        memory_str = ''
        user_name = Config.DEFAULT_USER

    # --- 3. START THE MAIN AGENT LOGIC ---
    # Initialize the agent with the loaded data
    assistant = MCPAssistant(mcp_tools, chat_ctx=initial_ctx)

    # Register the shutdown hook before starting the main loop
    ctx.add_shutdown_callback(
        lambda: shutdown_hook(assistant.chat_ctx, mem0, memory_str, user_name)
    )

    # Start the main agent session loop in a background task
    session_task = asyncio.create_task(session.start(
        agent=assistant,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            video_enabled=True,
            audio_enabled=False,
            noise_cancellation=noise_cancellation.BVC()
        )
    ))

    # Yield control to the event loop to allow the session_task to start
    await asyncio.sleep(0)

    # Generate an initial greeting now that the session is running
    greeting_instructions = "Hi! I'm A.R.I.A - Lightning-Fast AI Concierge"
    await session.generate_reply(instructions=greeting_instructions)

    # Wait for the session task to complete (it won't, but this keeps the entrypoint alive)
    await session_task


if __name__ == "__main__":
    print("🎙️ MCP Voice Agent with Mem0 Memory Starting…")
    opts = WorkerOptions(entrypoint_fnc=entrypoint)
    cli.run_app(opts)
