"""Data models for market data."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Market:
    """Represents a prediction market."""
    id: str
    name: str
    question: str
    volume_24h: float
    liquidity: float
    price: Optional[float] = None
    created_at: Optional[datetime] = None
    
    def __str__(self) -> str:
        return f"Market({self.name[:50]}... vol=${self.volume_24h:,.0f})"


@dataclass
class PriceUpdate:
    """Represents a price update event."""
    token_id: str
    market_name: str
    old_price: float
    new_price: float
    timestamp: datetime
    
    @property
    def change_pct(self) -> float:
        """Calculate percentage change."""
        if self.old_price == 0:
            return 0.0
        return (self.new_price - self.old_price) / self.old_price
    
    @property
    def change_abs(self) -> float:
        """Calculate absolute change."""
        return self.new_price - self.old_price
    
    def __str__(self) -> str:
        return f"PriceUpdate({self.market_name}: ${self.old_price:.3f} → ${self.new_price:.3f} [{self.change_pct:+.2%}])"
