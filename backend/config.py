import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Environment variable validation
REQUIRED_KEYS = [ 
    "DEEPGRAM_API_KEY",  
    "COMPOSIO_MCP_URL",
    "MEM0_API_KEY",
    "OPENROUTER_API_KEY"
]

def validate_environment():
    """Validate required environment variables"""
    missing = [k for k in REQUIRED_KEYS if not os.getenv(k)]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")
    
    # Validate MCP URL format
    composio_url = os.getenv("COMPOSIO_MCP_URL", "")
    if not composio_url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid COMPOSIO_MCP_URL format: {composio_url}")

# API Configuration
class Config:
    # MCP Configuration
    COMPOSIO_MCP_URL = os.getenv("COMPOSIO_MCP_URL", "")
    N8N_MCP_SERVER_URL = os.getenv("N8N_MCP_SERVER_URL", "")
    
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    MEM0_API_KEY = os.getenv("MEM0_API_KEY")
    TAVUS_API_KEY = os.getenv("TAVUS_API_KEY")
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL = "openai/gpt-4.1-mini"
    
    # Agent Configuration
    DEFAULT_USER = "default_user"
    
    # Tavus Avatar Configuration
    AVATAR_REPLICA_ID = "r9c55f9312fb"
    AVATAR_PERSONA_ID = "p92e6cb9cbb2"
    
    # TTS Configuration
    CARTESIA_VOICE_ID = "996a8b96-4804-46f0-8e05-3fd4ef1a87cd"
    CARTESIA_MODEL = "sonic-2"
    
    # Model Configuration
    LLM_TEMPERATURE = 0.7
    LLM_TIMEOUT = 45.0
