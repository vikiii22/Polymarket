import logging
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.constants import POLYGON
import config

# SILENCIAR LOGS DE LIBRERÍAS EXTERNAS
# Esto elimina los "HTTP Request: GET..." que ensucian la consola
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

class PolymarketClient:
    def __init__(self):
        self.host = "https://clob.polymarket.com"
        
        # Validate private key before attempting to create client
        if config.PRIVATE_KEY:
            try:
                self.client = ClobClient(self.host, key=config.PRIVATE_KEY, chain_id=POLYGON)
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
                raise RuntimeError(
                    f"❌ Failed to initialize Polymarket client: {e}\n"
                    "   Check your PRIVATE_KEY and network connection."
                ) from e
        else:
            # No private key provided - create client without authentication
            # This will work for read-only operations (getting prices)
            self.client = ClobClient(self.host, chain_id=POLYGON)
        
        if config.CLOB_API_KEY:
            creds = ApiCreds(
                api_key=config.CLOB_API_KEY,
                api_secret=config.CLOB_API_SECRET,
                api_passphrase=config.CLOB_API_PASSPHRASE
            )
            self.client.set_api_creds(creds)

    def get_mid_price(self, token_id):
        """Calcula el precio medio si hay liquidez."""
        try:
            ob = self.client.get_order_book(token_id)
            # Verificamos que existan tanto compradores (bids) como vendedores (asks)
            if not ob or not hasattr(ob, 'bids') or not ob.bids or not ob.asks:
                return None
            
            if len(ob.bids) == 0 or len(ob.asks) == 0:
                return None

            best_bid = float(ob.bids[0].price)
            best_ask = float(ob.asks[0].price)
            return (best_bid + best_ask) / 2
        except Exception:
            return None
