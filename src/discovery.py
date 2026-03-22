import requests
import logging
import json

logger = logging.getLogger(__name__)

class MarketDiscovery:
    def __init__(self):
        self.gamma_url = "https://gamma-api.polymarket.com/markets"

    def _safe_float(self, val):
        """Convierte a float de forma segura evitando errores de tipos."""
        try:
            return float(val) if val is not None else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _parse_json_field(self, field_data):
        """
        La API de Gamma a veces devuelve listas como strings "[val1, val2]".
        Esta función asegura que siempre obtengamos una lista de Python.
        """
        if isinstance(field_data, list):
            return field_data
        if isinstance(field_data, str):
            try:
                return json.loads(field_data)
            except:
                return []
        return []

    def get_trending_markets(self, limit=10):
        """
        Busca los mercados activos con más volumen (Trending).
        """
        params = {
            "active": "true",
            "closed": "false",
            "order": "volume24hr",
            "ascending": "false",
            "limit": limit
        }

        try:
            response = requests.get(self.gamma_url, params=params)
            response.raise_for_status()
            markets = response.json()

            discovery_results = []
            for m in markets:
                # 1. Parsear IDs de Tokens
                token_ids = self._parse_json_field(m.get("clobTokenIds"))
                if not token_ids:
                    continue
                
                yes_token_id = token_ids[0]

                # 2. Parsear Precios (Evita el error del '[' )
                prices = self._parse_json_field(m.get("outcomePrices"))
                current_price = self._safe_float(prices[0]) if prices else 0.0

                # 3. Parsear métricas de volumen y liquidez
                volume = self._safe_float(m.get("volume24hr"))
                liquidity = self._safe_float(m.get("liquidity"))

                discovery_results.append({
                    "id": yes_token_id,
                    "name": m.get("question", "Desconocido"),
                    "volume": volume,
                    "liquidity": liquidity,
                    "price": current_price
                })
            
            return discovery_results

        except Exception as e:
            logger.error(f"Error descubriendo mercados: {e}")
            return []

    def print_ranking(self, markets):
        """Muestra un ranking profesional en consola."""
        print("\n" + "🏆 RANKING DE MERCADOS EN TENDENCIA".center(75))
        print("-" * 85)
        print(f"{'Rank':<5} | {'Mercado':<45} | {'Vol. 24h':>12} | {'Precio'}")
        print("-" * 85)
        
        # Ordenamos por volumen (Liquidez = Rentabilidad)
        sorted_markets = sorted(markets, key=lambda x: x['volume'], reverse=True)
        
        for i, m in enumerate(sorted_markets, 1):
            name_short = (m['name'][:42] + '..') if len(m['name']) > 42 else m['name']
            # Resaltamos el precio si es barato (potencial rentabilidad)
            price_str = f"${m['price']:.2f}"
            print(f"#{i:<4} | {name_short:<45} | ${m['volume']:>11.0f} | {price_str}")
        print("-" * 85 + "\n")
