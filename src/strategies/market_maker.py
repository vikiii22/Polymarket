import logging
from strategies.base import BaseStrategy

logger = logging.getLogger(__name__)

class BasicMarketMaker(BaseStrategy):
    def __init__(self, client, risk_manager, orderbook_data):
        self.client = client
        self.risk = risk_manager
        self.orderbook_data = orderbook_data

    async def evaluate(self):
        """Evaluar datos de Bids y Asks en crudo para tomar decisiones de MM"""
        bids = self.orderbook_data.get("bids", [])
        asks = self.orderbook_data.get("asks", [])
        
        if not bids or not asks:
            return
            
        # Parse price y sizes del string que retorna la API
        best_bid = float(bids[0]["price"]) if bids else 0.0
        best_ask = float(asks[0]["price"]) if asks else 1.0
        spread = best_ask - best_bid
        
        logger.info(f"[MM Strategy] Best Bid: {best_bid:.3f} | Best Ask: {best_ask:.3f} | Spread: {spread:.3f}")
        
        # Ejecutar micro-lógica: Si el spread es amplio y podemos mejorar la punta
        if spread > 0.05: # Spread de 5 centavos
            logger.info("Spread amplio detectado: Posible oportunidad MM.")
            # Calcula el capital a colocar
            # position = self.risk.calculate_position_size(...)
            pass
