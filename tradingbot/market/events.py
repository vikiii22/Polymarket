"""Event models for real-time updates."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class EventType(Enum):
    """Types of events that can be emitted."""
    PRICE_UPDATE = "price_update"
    VOLATILITY_ALERT = "volatility_alert"
    ORDER_FILLED = "order_filled"
    ERROR = "error"


@dataclass
class Event:
    """Base event class."""
    event_type: EventType
    timestamp: datetime
    data: dict
    
    def __str__(self) -> str:
        return f"Event({self.event_type.value} at {self.timestamp})"


@dataclass
class PriceUpdateEvent(Event):
    """Event emitted when a price changes."""
    token_id: str
    market_name: str
    old_price: float
    new_price: float
    change_pct: float
    
    def __init__(
        self,
        token_id: str,
        market_name: str,
        old_price: float,
        new_price: float
    ):
        self.token_id = token_id
        self.market_name = market_name
        self.old_price = old_price
        self.new_price = new_price
        self.change_pct = (new_price - old_price) / old_price if old_price > 0 else 0.0
        
        super().__init__(
            event_type=EventType.PRICE_UPDATE,
            timestamp=datetime.now(),
            data={
                "token_id": token_id,
                "market_name": market_name,
                "old_price": old_price,
                "new_price": new_price,
                "change_pct": self.change_pct
            }
        )


@dataclass
class VolatilityAlertEvent(Event):
    """Event emitted when volatility threshold is exceeded."""
    token_id: str
    market_name: str
    old_price: float
    new_price: float
    change_pct: float
    threshold: float
    
    def __init__(
        self,
        token_id: str,
        market_name: str,
        old_price: float,
        new_price: float,
        threshold: float
    ):
        self.token_id = token_id
        self.market_name = market_name
        self.old_price = old_price
        self.new_price = new_price
        self.threshold = threshold
        self.change_pct = (new_price - old_price) / old_price if old_price > 0 else 0.0
        
        super().__init__(
            event_type=EventType.VOLATILITY_ALERT,
            timestamp=datetime.now(),
            data={
                "token_id": token_id,
                "market_name": market_name,
                "old_price": old_price,
                "new_price": new_price,
                "change_pct": self.change_pct,
                "threshold": threshold
            }
        )
