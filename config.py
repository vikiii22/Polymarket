import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CLOB_API_KEY = os.getenv("CLOB_API_KEY")
CLOB_API_SECRET = os.getenv("CLOB_API_SECRET")
CLOB_API_PASSPHRASE = os.getenv("CLOB_API_PASSPHRASE")

# Trading Parameters
TARGET_TOKEN_ID = os.getenv("TARGET_TOKEN_ID")
DRY_RUN = os.getenv("DRY_RUN", "True").lower() == "true"

# Strategy Defaults
SPREAD = 0.02  # 2% spread
MIN_SPREAD = 0.005  # 0.5% minimum spread to operate
ORDER_SIZE = 10.0  # $10 USDC per order
MAX_POSITION = 50.0  # Max exposure in USDC (max shares held)
SLEEP_INTERVAL = 5  # Seconds between updates

# Simulation/Performance Tracking
INITIAL_BALANCE = 10.0  # Starting simulation balance in USDC
BALANCE_LOG_FILE = "balance_history.txt"
POSITION_FILE = "current_position.json"

if not PRIVATE_KEY and not DRY_RUN:
    print("WARNING: PRIVATE_KEY not found. Running in DRY_RUN mode only.")
    DRY_RUN = True
