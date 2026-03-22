"""Data models for API responses and requests."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class OrderBookEntry:
    """Represents a single order in the order book."""
    price: float
    size: float


@dataclass
class OrderBook:
    """Represents the full order book for a market."""
    token_id: str
    bids: List[OrderBookEntry]
    asks: List[OrderBookEntry]
    timestamp: Optional[float] = None
    
    @property
    def best_bid(self) -> Optional[float]:
        """Get the best (highest) bid price."""
        return self.bids[0].price if self.bids else None
    
    @property
    def best_ask(self) -> Optional[float]:
        """Get the best (lowest) ask price."""
        return self.asks[0].price if self.asks else None
    
    @property
    def mid_price(self) -> Optional[float]:
        """Calculate the mid price between best bid and ask."""
        if self.best_bid is not None and self.best_ask is not None:
            return (self.best_bid + self.best_ask) / 2
        return None


@dataclass
class Position:
    """Represents a trading position."""
    token_id: str
    size: float
    average_price: float
    market_value: Optional[float] = None


@dataclass
class Balance:
    """Represents account balance."""
    asset: str
    balance: float
    available: float
