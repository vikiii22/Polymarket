from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, ApiCreds
from py_clob_client.constants import POLYGON
from py_clob_client.exceptions import PolyApiException

import config
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def sanitize(val):
    return str(val or "").strip().replace('"', '').replace("'", "")

class PolymarketClient:
    def __init__(self):
        self.host = "https://clob.polymarket.com"
        self.chain_id = POLYGON
        self.dry_run = config.DRY_RUN

        try:
            # 1. Clean Keys
            priv_key = sanitize(config.PRIVATE_KEY)
            if priv_key.lower().startswith('0x'):
                priv_key = priv_key[2:]
            
            api_key = sanitize(config.CLOB_API_KEY)
            api_secret = sanitize(config.CLOB_API_SECRET)
            api_passphrase = sanitize(config.CLOB_API_PASSPHRASE)

            if len(priv_key) == 64:
                # Initialize with L1 first
                self.client = ClobClient(
                    host=self.host, 
                    key=priv_key, 
                    chain_id=self.chain_id
                )
                
                # IMPORTANT: Print the wallet address so user can verify
                self.address = self.client.get_address()
                logger.info(f"!!! TU DIRECCION DE WALLET ES: {self.address} !!!")
                logger.info("VERIFICA: ¿Es esta la misma dirección que ves en Polymarket.com -> Settings?")

                if api_key and api_secret:
                    # Initialize Creds object
                    creds = ApiCreds(
                        api_key=api_key,
                        api_secret=api_secret,
                        api_passphrase=api_passphrase
                    )
                    # Set credentials explicitly
                    self.client.set_api_creds(creds)
                    logger.info("Polymarket Client: API Credentials set. Testing...")
                else:
                    logger.warning("No API Keys found in .env. Bot will run in L1/Read-Only mode.")
            else:
                self.client = ClobClient(self.host)
                logger.info("Polymarket Client: READ-ONLY (No Private Key)")
                
        except Exception as e:
            logger.error(f"Critical error during client init: {e}")
            raise

    def get_balances(self):
        """Fetch USDC balance with fallback for empty accounts."""
        try:
            # get_balance_allowance often fails if account is not 'onboarded' or has 0 funds
            resp = self.client.get_balance_allowance()
            if resp:
                return [{"asset": "USDC", "balance": float(resp.get("balance", 0.0))}]
            return [{"asset": "USDC", "balance": 0.0}]
        except Exception as e:
            if "401" in str(e):
                logger.error("ERROR 401: Tus API Keys son rechazadas. ¿Las generaste para esta misma wallet?")
            else:
                logger.warning(f"Balance info unavailable (Account likely empty): {e}")
            return [{"asset": "USDC", "balance": 0.0}]

    def get_positions(self):
        """Fetch current positions."""
        try:
            if hasattr(self.client, 'get_positions'):
                return self.client.get_positions()
            return [] 
        except Exception:
            return []

    def get_order_book(self, token_id):
        """Fetch the order book."""
        try:
            return self.client.get_order_book(token_id)
        except Exception as e:
            logger.error(f"Error fetching order book: {e}")
            return None

    def get_mid_price(self, token_id):
        """Calculate mid-price."""
        ob = self.get_order_book(token_id)
        if not ob or not hasattr(ob, 'bids') or not ob.bids or not ob.asks:
            return None
        best_bid = float(ob.bids[0].price)
        best_ask = float(ob.asks[0].price)
        return (best_bid + best_ask) / 2

    def place_limit_order(self, token_id, price, size, side):
        """Place a limit order."""
        if self.dry_run:
            logger.info(f"[DRY RUN] {side} {size} shares at ${price:.2f}")
            return None
        try:
            order_args = OrderArgs(
                price=round(float(price), 2),
                size=round(float(size), 2),
                side=side.upper(),
                token_id=token_id
            )
            return self.client.create_and_post_order(order_args)
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None

    def cancel_all(self):
        """Cancel all orders."""
        if not self.dry_run:
            try:
                self.client.cancel_all()
                logger.info("All orders cancelled.")
            except Exception as e:
                if "401" in str(e):
                    # Only log once to avoid spam
                    pass 
                else:
                    logger.error(f"Error cancelling orders: {e}")
