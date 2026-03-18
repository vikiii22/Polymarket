import time
import logging
import sys
from client import PolymarketClient
from strategy import MarketMaker
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log")
    ]
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Polymarket Trading Bot...")
    
    # 1. Validate Configuration
    if not config.TARGET_TOKEN_ID:
        logger.error("TARGET_TOKEN_ID is missing in .env file.")
        logger.info("Please set TARGET_TOKEN_ID to the market token ID you want to trade.")
        sys.exit(1)

    if config.DRY_RUN:
        logger.info("Running in DRY_RUN mode. No real orders will be placed.")
    else:
        logger.warning("Running in LIVE mode. Real orders WILL be placed!")
        logger.warning("Press Ctrl+C immediately if this is unintentional.")
        time.sleep(5)  # Give user a chance to cancel

    # 2. Initialize Client
    try:
        client = PolymarketClient()
        # Verify connection by fetching order book
        ob = client.get_order_book(config.TARGET_TOKEN_ID)
        if ob:
            logger.info(f"Successfully connected to market: {config.TARGET_TOKEN_ID}")
        else:
            logger.error("Failed to fetch initial market data. Check TOKEN_ID and connection.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Failed to initialize client: {e}")
        sys.exit(1)

    # 3. Initialize Strategy
    strategy = MarketMaker(client, config.TARGET_TOKEN_ID)
    
    # 4. Main Loop
    logger.info("Entering main trading loop. Press Ctrl+C to stop.")
    try:
        while True:
            strategy.run_cycle()
            time.sleep(config.SLEEP_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
        # Attempt to cancel all orders on exit (safety)
        if not config.DRY_RUN:
            logger.info("Cancelling open orders...")
            try:
                client.cancel_all()
            except:
                pass
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
