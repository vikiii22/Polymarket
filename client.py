from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.constants import POLYGON
from py_clob_client.exceptions import PolyApiException

import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PolymarketClient:
    def __init__(self):
        self.host = "https://clob.polymarket.com"
        self.chain_id = POLYGON
        self.dry_run = config.DRY_RUN

        # Initialize client with optional credentials
        try:
            is_valid_key = config.PRIVATE_KEY and len(config.PRIVATE_KEY) >= 64 and all(c in "0123456789abcdefABCDEF" for c in config.PRIVATE_KEY.replace("0x", ""))
            
            if is_valid_key:
                self.client = ClobClient(
                    self.host, 
                    key=config.PRIVATE_KEY, 
                    chain_id=self.chain_id
                )
                logger.info("Polymarket Client initialized (Authenticated)")
            else:
                self.client = ClobClient(self.host)
                logger.info("Polymarket Client initialized (Read-Only/Public Mode)")
        except Exception as e:
            logger.error(f"Failed to initialize client: {e}")
            raise

    def _get_creds(self):
        # If user provided API keys, use them. Otherwise, client might derive them (if implemented)
        # For simplicity, we'll return None and let py-clob-client handle it if possible, 
        # or rely on basic key signing (L1).
        # To use L2, you'd need to create/derive creds.
        if config.CLOB_API_KEY and config.CLOB_API_SECRET and config.CLOB_API_PASSPHRASE:
             # Structure required by py-clob-client might vary, check docs.
             # Assuming standard format or letting client derive if needed.
             return None # Placeholder: implementation depends on exact library version
        return None

    def get_order_book(self, token_id):
        """Fetch the order book for a given token."""
        try:
            return self.client.get_order_book(token_id)
        except Exception as e:
            logger.error(f"Error fetching order book: {e}")
            return None

    def get_mid_price(self, token_id):
        """Calculate the mid-price based on the best bid and ask."""
        ob = self.get_order_book(token_id)
        if not ob or not ob.bids or not ob.asks:
            return None
        
        best_bid = float(ob.bids[0].price)
        best_ask = float(ob.asks[0].price)
        return (best_bid + best_ask) / 2

    def place_limit_order(self, token_id, price, size, side):
        """Place a limit order (or simulate it)."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would place {side} order: {size} shares of {token_id} at ${price:.2f}")
            return {"status": "simulated", "orderID": "sim-123"}
        
        try:
            # Check balance/allowance logic would go here
            logger.info(f"Placing {side} order: {size} shares at ${price:.2f}")
            
            # Construct order arguments using the library's types
            order_args = OrderArgs(
                price=price,
                size=size,
                side=side.upper(),
                token_id=token_id
            )
            
            resp = self.client.create_and_post_order(order_args)
            logger.info(f"Order placed successfully: {resp.get('orderID')}")
            return resp
            
        except PolyApiException as e:
            logger.error(f"API Error placing order: {e}")
        except Exception as e:
            logger.error(f"Unexpected error placing order: {e}")
        return None

    def cancel_all(self):
        """Cancel all open orders (safety)."""
        if self.dry_run:
            logger.info("[DRY RUN] Would cancel all open orders")
            return
        
        try:
            self.client.cancel_all()
            logger.info("Cancelled all open orders")
        except Exception as e:
            logger.error(f"Error cancelling orders: {e}")
