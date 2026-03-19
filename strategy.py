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
        
        # Real-time Tracking from API
        self.cash = 0.0
        self.shares = 0.0
        self.update_real_balances()
        self._log_balance()

    def update_real_balances(self):
        """Fetch actual USDC balance and share position from Polymarket API."""
        try:
            # Get real USDC balance (assuming USDC is the collateral)
            # Note: This requires an authenticated client
            balances = self.client.get_balances() 
            if balances:
                # Find USDC balance in the list of balances
                usdc_balance = next((b for b in balances if b.get('asset') == 'USDC'), None)
                if usdc_balance:
                    self.cash = float(usdc_balance.get('balance', 0.0))
            
            # Get real position in the specific token
            positions = self.client.get_positions()
            if positions:
                token_pos = next((p for p in positions if p.get('token_id') == self.token_id), None)
                if token_pos:
                    self.shares = float(token_pos.get('size', 0.0))
            
            logger.info(f"REAL BALANCE: Cash=${self.cash:.2f}, Shares={self.shares}")
        except Exception as e:
            logger.error(f"Error fetching real balances: {e}. Falling back to 0 or cached.")

    def _log_balance(self, mid_price=None):
        """Write current REAL balance to TXT file."""
        if mid_price is None:
            mid_price = self.client.get_mid_price(self.token_id) or 0.5
            
        portfolio_value = self.cash + (self.shares * mid_price)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] REAL Cash: ${self.cash:.2f} | REAL Shares: {self.shares:.2f} | Portfolio Val: ${portfolio_value:.2f} | Mid-Price: {mid_price:.3f}\n"
        
        with open(BALANCE_LOG_FILE, "a") as f:
            f.write(log_line)
        logger.info(f"MARKET VALUE: ${portfolio_value:.2f} (${self.cash:.2f} cash + {self.shares:.2f} shares)")

    def run_cycle(self):
        """Execute one cycle with real market data and order placement."""
        logger.info(f"--- Strategy Cycle for {self.token_id} ---")

        # 1. Update balances from the blockchain/API
        self.update_real_balances()

        # 2. Get Market Data
        ob = self.client.get_order_book(self.token_id)
        if not ob:
            return

        bids = ob.bids if hasattr(ob, 'bids') and ob.bids else []
        asks = ob.asks if hasattr(ob, 'asks') and ob.asks else []
        if not (bids and asks):
            return

        best_bid = float(bids[0].price)
        best_ask = float(asks[0].price)
        mid_price = (best_bid + best_ask) / 2

        # 3. Calculate Our Quotes (Prices we would offer)
        # We place orders around the mid-price to capture the spread
        my_bid = mid_price * (1 - self.spread / 2)
        my_ask = mid_price * (1 + self.spread / 2)
        
        # Risk Management: Inventory Skewing
        # If we have too many shares, we want to sell (lower our ask to be more competitive)
        if self.shares > self.max_position * 0.7:
            logger.info("High exposure: Skewing prices to SELL.")
            my_bid *= 0.95  # Buy much cheaper if we have too many
            my_ask *= 0.99  # Sell slightly cheaper to unload inventory

        # 4. Order Execution
        # Cancel old orders and place new ones based on updated mid-price
        self.client.cancel_all()
        
        # Only place BUY order if we have enough cash and haven't hit max position
        if self.cash >= (my_bid * self.order_size) and self.shares < self.max_position:
            self.client.place_limit_order(self.token_id, round(my_bid, 2), self.order_size, "BUY")
        
        # Only place SELL order if we actually have shares to sell
        if self.shares >= self.order_size:
            self.client.place_limit_order(self.token_id, round(my_ask, 2), self.order_size, "SELL")
        
        self._log_balance(mid_price)
        logger.info(f"Quotes: Bid=${my_bid:.3f}, Ask=${my_ask:.3f} | REAL Inventory: {self.shares} shares")
