import os
import json
import logging
import random
from datetime import datetime
from config import SPREAD, ORDER_SIZE, MAX_POSITION, INITIAL_BALANCE, BALANCE_LOG_FILE, POSITION_FILE

logger = logging.getLogger(__name__)

class MarketMaker:
    def __init__(self, client, token_id):
        self.client = client
        self.token_id = token_id
        self.spread = SPREAD
        self.order_size = ORDER_SIZE
        self.max_position = MAX_POSITION
        
        # Performance Tracking
        self.cash = INITIAL_BALANCE
        self.shares = 0.0
        self._load_position()
        self._log_balance()

    def _load_position(self):
        """Load simulated position from file if it exists."""
        if os.path.exists(POSITION_FILE):
            try:
                with open(POSITION_FILE, 'r') as f:
                    data = json.load(f)
                    self.cash = data.get('cash', INITIAL_BALANCE)
                    self.shares = data.get('shares', 0.0)
                    logger.info(f"Loaded simulation: Cash=${self.cash:.2f}, Shares={self.shares}")
            except Exception as e:
                logger.error(f"Error loading position: {e}")

    def _save_position(self):
        """Save simulated position to file."""
        try:
            with open(POSITION_FILE, 'w') as f:
                json.dump({'cash': self.cash, 'shares': self.shares}, f)
        except Exception as e:
            logger.error(f"Error saving position: {e}")

    def _log_balance(self, mid_price=0.5):
        """Write current simulated balance to TXT file."""
        portfolio_value = self.cash + (self.shares * mid_price)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] Cash: ${self.cash:.2f} | Shares: {self.shares:.2f} | Portfolio Val: ${portfolio_value:.2f} | Mid-Price: {mid_price:.3f}\n"
        
        with open(BALANCE_LOG_FILE, "a") as f:
            f.write(log_line)
        logger.info(f"PERFORMANCE: ${portfolio_value:.2f} (${self.cash:.2f} cash + {self.shares:.2f} shares)")

    def run_cycle(self):
        """Execute one cycle with simulated order filling."""
        logger.info(f"--- Strategy Cycle for {self.token_id} ---")

        # 1. Get Market Data
        ob = self.client.get_order_book(self.token_id)
        if not ob:
            return

        bids = ob.bids if hasattr(ob, 'bids') and ob.bids else []
        asks = ob.asks if hasattr(ob, 'asks') and ob.asks else []
        if not bids or not asks:
            return

        best_bid = float(bids[0].price)
        best_ask = float(asks[0].price)
        mid_price = (best_bid + best_ask) / 2

        # 2. Calculate Our Quotes (Prices we would offer)
        my_bid = mid_price * (1 - self.spread / 2)
        my_ask = mid_price * (1 + self.spread / 2)
        
        # Risk Adjustment: If we have many shares, raise the ask to sell, lower bid to stop buying
        if self.shares > self.max_position * 0.7:
            logger.info("High exposure: Skewing prices to SELL.")
            my_bid *= 0.98  # Offer to buy at a lower price
            my_ask *= 0.99  # Offer to sell at a slightly lower (more competitive) price

        # 3. Simulated Fill (Dry Run Logic)
        # We simulate a "profitable" fill by using our own bid/ask spread
        # There's a 10% chance to fill an order in each 5-second cycle
        if random.random() < 0.1: 
             # Simulating a buy: we pay the price we offered (my_bid)
             if self.cash >= (my_bid * self.order_size) and self.shares < self.max_position:
                 cost = my_bid * self.order_size
                 self.cash -= cost
                 self.shares += self.order_size
                 logger.info(f"SIM-FILL: Bought {self.order_size} shares at your Bid ${my_bid:.3f}. Cost: ${cost:.2f}")
             
             # Simulating a sell: we receive the price we offered (my_ask)
             elif self.shares >= self.order_size:
                 revenue = my_ask * self.order_size
                 self.cash += revenue
                 self.shares -= self.order_size
                 logger.info(f"SIM-FILL: Sold {self.order_size} shares at your Ask ${my_ask:.3f}. Revenue: ${revenue:.2f}")
        
        self._save_position()
        self._log_balance(mid_price)

        logger.info(f"Current Quotes: Bid=${my_bid:.3f}, Ask=${my_ask:.3f} | Inventory: {self.shares} shares")
        
        # Place simulation orders in CLI
        self.client.cancel_all()
        self.client.place_limit_order(self.token_id, my_bid, self.order_size, "BUY")
        self.client.place_limit_order(self.token_id, my_ask, self.order_size, "SELL")
