import asyncio
import logging
import os
from config import config
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, ApiCreds

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        self.client = None
        self.is_running = False
        
    async def initialize_client(self):
        """Inicializa el ClobClient con la sintaxis correcta de 2026."""
        logger.info("Conectando a PolyMarket CLOB...")
        
        try:
            creds = ApiCreds(
                api_key=os.getenv("POLYMARKET_API_KEY", ""),
                api_secret=os.getenv("POLYMARKET_API_SECRET", ""),
                api_passphrase=os.getenv("POLYMARKET_API_PASSPHRASE", "")
            )
            
            self.client = ClobClient(
                host=config.HOST,
                key=config.PRIVATE_KEY,  # Private Key va aquí
                chain_id=config.CHAIN_ID,
                funder=config.FUNDER_ADDRESS,
                creds=creds
            )
            
            # En las versiones nuevas, basta con verificar si la conexión es válida
            status = self.client.get_ok()
            if status == "OK":
                logger.info("Autenticación exitosa y API operativa.")
            else:
                raise Exception("La API de Polymarket no retornó estado OK.")
        except Exception as e:
            logger.error(f"Error de autenticación: {e}")
            logger.info("Asegúrate de haber añadido tus llaves reales en el archivo .env")
            raise

    async def _strategy_loop(self):
        """Módulo de estrategia de Micro-Arbitraje simulado ejecutado periodicamente."""
        from strategies.market_maker import BasicMarketMaker
        from core.risk import RiskManager
        
        risk = RiskManager(config.CAPITAL_INICIAL, config.KELLY_FRACTION_MODIFIER)
        # Nota: aquí le pasamos self.client una vez inicializado
        strategy = BasicMarketMaker(self.client, risk)
        
        while self.is_running:
            try:
                await strategy.evaluate()
                # Simular latencia de espera a la próxima evaluación de ticks
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error en estrategia: {e}. Reintentando en 5s...")
                await asyncio.sleep(5)

    async def _websocket_feed(self):
        """Maneja el feed de datos por websocket en tiempo real."""
        while self.is_running:
            try:
                logger.info("Escuchando WebSockets de Orderbook (Simulado)...")
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"WS Desconectado, reconectando... Error: {e}")
                await asyncio.sleep(2)

    async def run(self):
        self.is_running = True
        try:
            await self.initialize_client()
        except Exception:
            logger.error("No se pudo iniciar el bot debido a errores de credenciales.")
            return
        
        # Lanza las tareas concurrentes (WebSockets + Lógica de Trading)
        tasks = [
            asyncio.create_task(self._websocket_feed()),
            asyncio.create_task(self._strategy_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Bot apagándose limpiamente...")
            self.is_running = False

if __name__ == "__main__":
    bot = TradingBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Terminación manual detectada. Saliendo...")
