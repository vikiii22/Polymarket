"""Market monitor for tracking price changes and volatility."""

import json
import os
import time
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from .events import VolatilityAlertEvent
from ..notifications.notifier import AlertNotifier

logger = logging.getLogger(__name__)


class MarketMonitor:
    """
    Monitors market prices and detects volatility alerts.
    
    Tracks price changes over time and triggers alerts when volatility
    exceeds configured thresholds.
    """
    
    def __init__(
        self,
        client,
        threshold: float = 0.05,
        check_interval: int = 300,
        state_file: str = "data/prices_state.json"
    ):
        """
        Initialize market monitor.
        
        Args:
            client: Polymarket client instance
            threshold: Volatility threshold (e.g., 0.05 = 5%)
            check_interval: Seconds between price checks
            state_file: Path to price state persistence file
        """
        self.client = client
        self.threshold = threshold
        self.check_interval = check_interval
        self.state_file = state_file
        self.notifier = AlertNotifier()
        self.prices: Dict[str, float] = self._load_state()
        
        logger.info(
            f"Initialized MarketMonitor (threshold={threshold:.1%}, "
            f"interval={check_interval}s)"
        )

    def _load_state(self) -> Dict[str, float]:
        """
        Load price history from JSON file.
        
        Returns:
            Dictionary mapping token_id to last known price
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded price state for {len(data)} markets")
                    return data
            except Exception as e:
                logger.error(f"Error loading price state: {e}")
        
        # Create directory if it doesn't exist
        Path(self.state_file).parent.mkdir(parents=True, exist_ok=True)
        return {}

    def _save_state(self) -> None:
        """Save price state to JSON file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.prices, f, indent=4)
            logger.debug(f"Saved price state for {len(self.prices)} markets")
        except Exception as e:
            logger.error(f"Error saving price state: {e}")

    def check_market(self, token_id: str, market_name: str = "Unknown") -> None:
        """
        Check a single market for price changes and trigger alerts if needed.
        
        Args:
            token_id: Token ID to monitor
            market_name: Human-readable market name for alerts
        """
        current_price = self.client.get_mid_price(token_id)
        
        if current_price is None:
            logger.debug(f"No price available for {market_name} ({token_id})")
            return

        last_price = self.prices.get(token_id)

        if last_price is None:
            # First time seeing this market
            logger.info(f"Registering initial price for {market_name}: ${current_price:.3f}")
            self.prices[token_id] = current_price
            self._save_state()
            return

        # Calculate percentage change
        change_pct = (current_price - last_price) / last_price

        if abs(change_pct) >= self.threshold:
            # Volatility threshold exceeded!
            logger.warning(
                f"VOLATILITY ALERT: {market_name} changed {change_pct:+.2%} "
                f"(${last_price:.3f} → ${current_price:.3f})"
            )
            
            # Create and emit event
            event = VolatilityAlertEvent(
                token_id=token_id,
                market_name=market_name,
                old_price=last_price,
                new_price=current_price,
                threshold=self.threshold
            )
            
            # Notify via configured channels
            self.notifier.notify(market_name, last_price, current_price, change_pct)
            
            # Update baseline price for next alert
            self.prices[token_id] = current_price
            self._save_state()
        else:
            # Price stable - log silently
            logger.debug(
                f"{market_name}: ${current_price:.3f} (change: {change_pct:+.2%})"
            )

    def run_loop(self, markets_to_watch: Dict[str, str]) -> None:
        """
        Main monitoring loop - checks markets continuously.
        
        Args:
            markets_to_watch: Dictionary mapping token_id to market_name
        """
        print(f"\n{'='*80}")
        print(f"🎯 MONITOR ACTIVADO (Umbral: {self.threshold:.1%}, Intervalo: {self.check_interval}s)")
        print(f"   Monitoreando {len(markets_to_watch)} mercados")
        print(f"   Presiona Ctrl+C para detener")
        print(f"{'='*80}\n")
        
        try:
            cycle = 0
            while True:
                cycle += 1
                start_time = time.time()
                
                logger.info(f"Starting monitoring cycle #{cycle}")
                
                for token_id, name in markets_to_watch.items():
                    self.check_market(token_id, name)
                
                elapsed = time.time() - start_time
                logger.info(f"Cycle #{cycle} completed in {elapsed:.2f}s")
                
                # Wait for next cycle
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print(f"\n{'='*80}")
            print("👋 Monitor detenido por el usuario")
            print(f"{'='*80}\n")
            logger.info("Monitor stopped by user")
