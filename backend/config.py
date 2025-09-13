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
    
    
    # API Keys
    
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    MEM0_API_KEY = os.getenv("MEM0_API_KEY")
    TAVUS_API_KEY = os.getenv("TAVUS_API_KEY")
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY=""   # if using openrouter key, pass it here explicity, else you any livekii compatible llms, likce groq or openai without create a openai client
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL = "google/gemini-2.5-pro"
    
    # Agent Configuration
    DEFAULT_USER = "default_user"
    
    # Tavus Avatar Configuration
    AVATAR_REPLICA_ID = ""  # get from tavus.ai
    AVATAR_PERSONA_ID = ""  # get from tavus.ai
    
    # TTS Configuration
    CARTESIA_VOICE_ID = "996a8b96-4804-46f0-8e05-3fd4ef1a87cd"
    CARTESIA_MODEL = "sonic-2"
    
    # Model Configuration
    LLM_TEMPERATURE = 0.7
    LLM_TIMEOUT = 45.0
