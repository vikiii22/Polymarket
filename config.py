import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import validation utilities
try:
    from tradingbot.utils.validators import validate_private_key
except ImportError:
    # Fallback if running from root directory before restructuring
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from tradingbot.utils.validators import validate_private_key

# API Configuration
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CLOB_API_KEY = os.getenv("CLOB_API_KEY")
CLOB_API_SECRET = os.getenv("CLOB_API_SECRET")
CLOB_API_PASSPHRASE = os.getenv("CLOB_API_PASSPHRASE")

# Validate PRIVATE_KEY format
_key_valid, _key_message = validate_private_key(PRIVATE_KEY)
if not _key_valid and PRIVATE_KEY:
    print(f"⚠️  WARNING: {_key_message}")
    print("    Your PRIVATE_KEY format is invalid. It must be a 64-character hexadecimal string.")
    print("    Example: 'a1b2c3d4e5f67890...' (64 chars) or '0xa1b2c3d4e5f67890...' (66 chars with 0x)")
    print("    🔒 Forcing DRY_RUN mode for safety.")
    PRIVATE_KEY = None  # Clear invalid key to prevent usage

# Trading Parameters
TARGET_TOKEN_ID = os.getenv("TARGET_TOKEN_ID")
DRY_RUN = os.getenv("DRY_RUN", "True").lower() == "true"

# Telegram Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Alert Parameters
VOLATILITY_THRESHOLD = float(os.getenv("VOLATILITY_THRESHOLD", "0.05"))  # 5% by default
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "10"))

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

if not PRIVATE_KEY:
    if not DRY_RUN:
        print("⚠️  WARNING: PRIVATE_KEY not found or invalid. Running in DRY_RUN mode only.")
    DRY_RUN = True
