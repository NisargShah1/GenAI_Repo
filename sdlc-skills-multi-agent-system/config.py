import os
import logging
from dotenv import load_dotenv

# Load env file if it exists
load_dotenv()

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("skillforge")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///skillforge.db")

# Models configuration
# Using the requested model names
FLASH_MODEL = "gemini-2.5-flash"
PRO_MODEL = "gemini-2.5-pro"

# Ensure API Key is set
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY is not set in environment or .env file.")
    logger.warning("The system will not be able to generate sprint plans without a valid API key.")
