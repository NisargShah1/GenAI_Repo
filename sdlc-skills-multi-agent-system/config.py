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

# ---------------------------------------------------------------------------
# Vertex AI configuration
#
# The system authenticates against Gemini through Vertex AI. Both the ADK
# agents and the direct google-genai client read the standard Vertex/ADC
# environment variables, so we normalize them here (after load_dotenv) so a
# .env file is enough to configure everything:
#   - GOOGLE_CLOUD_PROJECT         : GCP project id (required)
#   - GOOGLE_CLOUD_LOCATION        : region, defaults to us-central1
#   - GOOGLE_APPLICATION_CREDENTIALS: path to the service-account key JSON file
# ---------------------------------------------------------------------------
def _is_truthy(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")

USE_VERTEX_AI = _is_truthy(os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "true"))
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Optional API-key fallback (only used when Vertex AI is explicitly disabled).
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if USE_VERTEX_AI:
    # Propagate the resolved settings so libraries that read the environment
    # directly (ADK agents, google-genai) pick up the same configuration.
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    os.environ["GOOGLE_CLOUD_LOCATION"] = GOOGLE_CLOUD_LOCATION
    if GOOGLE_CLOUD_PROJECT:
        os.environ["GOOGLE_CLOUD_PROJECT"] = GOOGLE_CLOUD_PROJECT
    if GOOGLE_APPLICATION_CREDENTIALS:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    if not GOOGLE_CLOUD_PROJECT:
        logger.warning("GOOGLE_CLOUD_PROJECT is not set. Vertex AI calls will fail without a project id.")
    if not GOOGLE_APPLICATION_CREDENTIALS:
        logger.warning(
            "GOOGLE_APPLICATION_CREDENTIALS is not set. Provide the path to a service-account "
            "key JSON file, or rely on ambient Application Default Credentials."
        )
    elif not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
        logger.warning(
            f"GOOGLE_APPLICATION_CREDENTIALS points to a missing file: {GOOGLE_APPLICATION_CREDENTIALS}"
        )
else:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY is not set and Vertex AI is disabled; the system cannot call Gemini.")


def get_genai_client():
    """Build a google-genai Client configured for Vertex AI (or API key fallback).

    Credentials are resolved via Application Default Credentials, which reads the
    service-account key file referenced by GOOGLE_APPLICATION_CREDENTIALS.
    """
    from google import genai

    if USE_VERTEX_AI:
        return genai.Client(
            vertexai=True,
            project=GOOGLE_CLOUD_PROJECT,
            location=GOOGLE_CLOUD_LOCATION,
        )
    return genai.Client(api_key=GEMINI_API_KEY)
