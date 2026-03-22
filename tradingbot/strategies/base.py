"""Base strategy abstract class."""

from abc import ABC, abstractmethod
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Strategy(ABC):
    """
    Abstract base class for trading strategies.
    
    All trading strategies should inherit from this class and implement
    the required methods.
    """
    
    def __init__(self, client, token_id: str, name: str = "BaseStrategy"):
        """
        Initialize the strategy.
        
        Args:
            client: Polymarket client instance
            token_id: Token ID to trade
            name: Strategy name for logging
        """
        self.client = client
        self.token_id = token_id
        self.name = name
        logger.info(f"Initialized {self.name} for token {token_id}")
    
    @abstractmethod
    def run_cycle(self) -> None:
        """
        Execute one cycle of the trading strategy.
        
        This method should contain the core logic of the strategy
        and is called repeatedly by the main loop.
        """
        pass
    
    @abstractmethod
    def should_buy(self, price: float, **kwargs) -> bool:
        """
        Determine if the strategy should place a buy order.
        
        Args:
            price: Current market price
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            True if should buy, False otherwise
        """
        pass
    
    @abstractmethod
    def should_sell(self, price: float, **kwargs) -> bool:
        """
        Determine if the strategy should place a sell order.
        
        Args:
            price: Current market price
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            True if should sell, False otherwise
        """
        pass
    
    def get_position_size(self) -> float:
        """
        Get the current position size.
        
        Returns:
            Position size (number of shares)
        """
        positions = self.client.get_positions()
        for pos in positions:
            if pos.token_id == self.token_id:
                return pos.size
        return 0.0
    
    def get_current_price(self) -> Optional[float]:
        """
        Get the current mid price for the token.
        
        Returns:
            Current price or None if unavailable
        """
        return self.client.get_mid_price(self.token_id)
