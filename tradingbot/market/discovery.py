"""Market discovery module for finding trending markets."""

import requests
import logging
import json
from typing import List, Dict, Any

from .models import Market

logger = logging.getLogger(__name__)


class MarketDiscovery:
    """Discovers and filters trending prediction markets."""
    
    def __init__(self, gamma_url: str = "https://gamma-api.polymarket.com/markets"):
        """
        Initialize market discovery.
        
        Args:
            gamma_url: Base URL for Gamma API
        """
        self.gamma_url = gamma_url
        logger.info(f"Initialized MarketDiscovery with URL: {gamma_url}")

    def _safe_float(self, val: Any) -> float:
        """
        Convert value to float safely, avoiding type errors.
        
        Args:
            val: Value to convert
            
        Returns:
            Float value or 0.0 if conversion fails
        """
        try:
            return float(val) if val is not None else 0.0
        except (ValueError, TypeError):
            logger.debug(f"Failed to convert {val} to float, returning 0.0")
            return 0.0

    def _parse_json_field(self, field_data: Any) -> List:
        """
        Parse JSON field that might be a string or list.
        
        Gamma API sometimes returns lists as JSON strings.
        
        Args:
            field_data: Data to parse
            
        Returns:
            List of values
        """
        if isinstance(field_data, list):
            return field_data
        if isinstance(field_data, str):
            try:
                return json.loads(field_data)
            except json.JSONDecodeError:
                logger.debug(f"Failed to parse JSON field: {field_data}")
                return []
        return []

    def get_trending_markets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch trending markets ordered by 24h volume.
        
        Args:
            limit: Maximum number of markets to return
            
        Returns:
            List of market dictionaries with id, name, volume, liquidity, price
        """
        params = {
            "active": "true",
            "closed": "false",
            "order": "volume24hr",
            "ascending": "false",
            "limit": limit
        }

        try:
            logger.info(f"Fetching top {limit} trending markets...")
            response = requests.get(self.gamma_url, params=params, timeout=10)
            response.raise_for_status()
            markets = response.json()

            discovery_results = []
            for m in markets:
                # Parse token IDs
                token_ids = self._parse_json_field(m.get("clobTokenIds"))
                if not token_ids:
                    logger.debug(f"Skipping market without token IDs: {m.get('question', 'Unknown')}")
                    continue
                
                yes_token_id = token_ids[0]

                # Parse prices (avoiding the '[' error)
                prices = self._parse_json_field(m.get("outcomePrices"))
                current_price = self._safe_float(prices[0]) if prices else 0.5

                # Parse metrics
                volume = self._safe_float(m.get("volume24hr"))
                liquidity = self._safe_float(m.get("liquidity"))

                discovery_results.append({
                    "id": yes_token_id,
                    "name": m.get("question", "Unknown Market"),
                    "volume": volume,
                    "liquidity": liquidity,
                    "price": current_price
                })
            
            logger.info(f"Found {len(discovery_results)} trending markets")
            return discovery_results

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch trending markets: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error discovering markets: {e}")
            return []

    def print_ranking(self, markets: List[Dict[str, Any]]) -> None:
        """
        Display a formatted ranking of markets in console.
        
        Args:
            markets: List of market dictionaries
        """
        print("\n" + "🏆 RANKING DE MERCADOS EN TENDENCIA".center(85))
        print("-" * 85)
        print(f"{'Rank':<5} | {'Mercado':<45} | {'Vol. 24h':>12} | {'Precio'}")
        print("-" * 85)
        
        # Sort by volume (higher = more liquid = more opportunities)
        sorted_markets = sorted(markets, key=lambda x: x.get('volume', 0), reverse=True)
        
        for i, m in enumerate(sorted_markets, 1):
            name = m.get('name', 'Unknown')
            name_short = (name[:42] + '...') if len(name) > 45 else name
            volume = m.get('volume', 0)
            price = m.get('price', 0.5)
            
            print(f"#{i:<4} | {name_short:<45} | ${volume:>11,.0f} | ${price:.2f}")
        
        print("-" * 85 + "\n")
        
    def get_market_details(self, markets: List[Dict[str, Any]]) -> List[Market]:
        """
        Convert market dictionaries to Market objects.
        
        Args:
            markets: List of market dictionaries
            
        Returns:
            List of Market objects
        """
        return [
            Market(
                id=m['id'],
                name=m['name'],
                question=m.get('question', m['name']),
                volume_24h=m.get('volume', 0),
                liquidity=m.get('liquidity', 0),
                price=m.get('price')
            )
            for m in markets
        ]
