import logging
from src.strategies.base import BaseStrategy

logger = logging.getLogger(__name__)

class BasicMarketMaker(BaseStrategy):
    def __init__(self, client, risk_manager):
        self.client = client
        self.risk = risk_manager

    async def evaluate(self):
        # TODO: Implementar lógica de market making o micro-arbitraje
        logger.info("BasicMarketMaker: Buscando discrepancias de liquidez...")
        pass
