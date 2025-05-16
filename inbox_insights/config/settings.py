import os
from pathlib import Path

# Base paths
# BASE_DIR = Path(__file__).parent.parent.parent
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
EMAILS_DIR = DATA_DIR / "emails"

# Gmail API settings
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

# Data processing settings
DUMP_FREQUENCY = 10
MAX_RESULTS_PER_PAGE = 500

# Create necessary directories
EMAILS_DIR.mkdir(parents=True, exist_ok=True) 