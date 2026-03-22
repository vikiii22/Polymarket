"""Polymarket CLOB client with improved error handling and type hints."""

import logging
from typing import Optional, List
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.constants import POLYGON

from .exceptions import ApiConnectionError, InvalidTokenIdError
from .models import OrderBook, OrderBookEntry, Position, Balance
from ..utils.decorators import retry_on_failure

# Get logger for this module
logger = logging.getLogger(__name__)


class PolymarketClient:
    """
    Enhanced Polymarket CLOB client with better error handling.
    
    Provides methods to interact with Polymarket's Central Limit Order Book (CLOB)
    including fetching prices, order books, and placing orders.
    """
    
    def __init__(
        self,
        private_key: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        api_passphrase: Optional[str] = None,
        host: str = "https://clob.polymarket.com"
    ):
        """
        Initialize the Polymarket client.
        
        Args:
            private_key: Ethereum private key for signing transactions (optional for read-only)
            api_key: CLOB API key (optional)
            api_secret: CLOB API secret (optional)
            api_passphrase: CLOB API passphrase (optional)
            host: CLOB API host URL
            
        Raises:
            ValueError: If private_key format is invalid
            ApiConnectionError: If unable to connect to the API
        """
        self.host = host
        
        try:
            # Create client with or without private key
            if private_key:
                self.client = ClobClient(self.host, key=private_key, chain_id=POLYGON)
                logger.info("Initialized authenticated Polymarket client")
            else:
                self.client = ClobClient(self.host, chain_id=POLYGON)
                logger.info("Initialized read-only Polymarket client (no private key)")
            
            # Set API credentials if provided
            if api_key and api_secret and api_passphrase:
                creds = ApiCreds(
                    api_key=api_key,
                    api_secret=api_secret,
                    api_passphrase=api_passphrase
                )
                self.client.set_api_creds(creds)
                logger.info("Set CLOB API credentials")
                
        except ValueError as e:
            error_msg = str(e)
            if "non-hexadecimal" in error_msg.lower() or "invalid" in error_msg.lower():
                raise ValueError(
                    f"❌ Invalid PRIVATE_KEY format: {error_msg}\n"
                    "   The PRIVATE_KEY must be a 64-character hexadecimal string.\n"
                    "   Example: 'a1b2c3d4e5f67890...' (64 chars) or '0xa1b2c3d4e5f67890...' (66 with 0x)\n"
                    "   Found in .env file appears to be invalid (possibly a UUID with hyphens?)."
                ) from e
            else:
                raise
        except Exception as e:
            raise ApiConnectionError(
                f"Failed to initialize Polymarket client: {e}"
            ) from e

    @retry_on_failure(max_retries=3, backoff=2.0)
    def get_mid_price(self, token_id: str) -> Optional[float]:
        """
        Calculate the mid price for a token if there is liquidity.
        
        Args:
            token_id: The token ID to get the price for
            
        Returns:
            Mid price (average of best bid and ask), or None if no liquidity
            
        Raises:
            InvalidTokenIdError: If the token ID is invalid
            ApiConnectionError: If unable to fetch order book
        """
        try:
            ob = self.client.get_order_book(token_id)
            
            # Verify order book has data
            if not ob or not hasattr(ob, 'bids') or not ob.bids or not ob.asks:
                logger.debug(f"No order book data for token {token_id}")
                return None
            
            if len(ob.bids) == 0 or len(ob.asks) == 0:
                logger.debug(f"No liquidity for token {token_id}")
                return None

            best_bid = float(ob.bids[0].price)
            best_ask = float(ob.asks[0].price)
            mid_price = (best_bid + best_ask) / 2
            
            logger.debug(
                f"Token {token_id}: bid={best_bid:.3f}, ask={best_ask:.3f}, mid={mid_price:.3f}"
            )
            return mid_price
            
        except AttributeError as e:
            logger.error(f"Invalid token ID or malformed response for {token_id}: {e}")
            raise InvalidTokenIdError(f"Invalid token ID: {token_id}") from e
        except Exception as e:
            logger.error(f"Failed to get mid price for {token_id}: {e}")
            raise ApiConnectionError(f"Failed to fetch price for {token_id}") from e

    @retry_on_failure(max_retries=2, backoff=1.5)
    def get_order_book(self, token_id: str) -> Optional[OrderBook]:
        """
        Get the full order book for a token.
        
        Args:
            token_id: The token ID to get the order book for
            
        Returns:
            OrderBook object or None if unavailable
        """
        try:
            ob = self.client.get_order_book(token_id)
            
            if not ob:
                return None
            
            bids = [OrderBookEntry(float(b.price), float(b.size)) for b in ob.bids]
            asks = [OrderBookEntry(float(a.price), float(a.size)) for a in ob.asks]
            
            return OrderBook(
                token_id=token_id,
                bids=bids,
                asks=asks
            )
            
        except Exception as e:
            logger.error(f"Failed to get order book for {token_id}: {e}")
            return None

    def get_balances(self) -> List[Balance]:
        """
        Get account balances (requires authenticated client).
        
        Returns:
            List of Balance objects
        """
        try:
            balances = self.client.get_balances()
            return [
                Balance(
                    asset=b.get('asset', 'UNKNOWN'),
                    balance=float(b.get('balance', 0.0)),
                    available=float(b.get('available', 0.0))
                )
                for b in balances
            ] if balances else []
        except Exception as e:
            logger.error(f"Failed to get balances: {e}")
            return []

    def get_positions(self) -> List[Position]:
        """
        Get current positions (requires authenticated client).
        
        Returns:
            List of Position objects
        """
        try:
            positions = self.client.get_positions()
            return [
                Position(
                    token_id=p.get('token_id', ''),
                    size=float(p.get('size', 0.0)),
                    average_price=float(p.get('average_price', 0.0))
                )
                for p in positions
            ] if positions else []
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []

    def cancel_all(self) -> bool:
        """
        Cancel all open orders.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.cancel_all()
            logger.info("Cancelled all open orders")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel orders: {e}")
            return False

    def place_limit_order(
        self,
        token_id: str,
        price: float,
        size: float,
        side: str
    ) -> bool:
        """
        Place a limit order.
        
        Args:
            token_id: Token to trade
            price: Limit price
            size: Order size
            side: "BUY" or "SELL"
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.place_limit_order(token_id, price, size, side)
            logger.info(f"Placed {side} order: {size} @ ${price:.3f} for {token_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return False
