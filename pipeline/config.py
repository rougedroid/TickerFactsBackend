from pathlib import Path
from dotenv import load_dotenv
import os

ROOT_DIR = Path(__file__).resolve().parent.parent
PIPELINE_DIR = ROOT_DIR / "pipeline"
TEMP_DIR = PIPELINE_DIR / "temp"
DB_PATH = PIPELINE_DIR / "storage" / "filings.db"

load_dotenv(ROOT_DIR / ".env")

SEC_USER_AGENT = os.getenv("SEC_USER_AGENT")
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("INTERNAL_API_KEY")

REQUEST_TIMEOUT = 30
POLL_INTERVAL = 30
MAX_RETRIES = 3