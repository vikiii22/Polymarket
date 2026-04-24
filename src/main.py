import asyncio
import logging
import os
import json
import websockets
from config import config
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, ApiCreds

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        self.client = None
        self.is_running = False
        self.orderbook_data = {"bids": [], "asks": []}
        
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
        """Módulo de estrategia de Micro-Arbitraje ejecutado periodicamente base a datos reales WS."""
        from strategies.market_maker import BasicMarketMaker
        from core.risk import RiskManager
        
        risk = RiskManager(config.CAPITAL_INICIAL, config.KELLY_FRACTION_MODIFIER)
        # Inyectamos client, risk, y la referencia a los datos del websocket (diccionario por referencia)
        strategy = BasicMarketMaker(self.client, risk, self.orderbook_data)
        
        while self.is_running:
            try:
                # Solo evalúa la estrategia si tenemos al menos algún lado del feed
                if len(self.orderbook_data["bids"]) > 0 or len(self.orderbook_data["asks"]) > 0:
                    await strategy.evaluate()
                
                # Evaluación agresiva con loop 1.5s
                await asyncio.sleep(1.5)
                
            except Exception as e:
                logger.error(f"Error en estrategia: {e}. Reintentando en 5s...")
                await asyncio.sleep(5)

    async def _websocket_feed(self):
        """Maneja el feed de datos por websocket en tiempo real a CLOB Polymarket WS."""
        ws_url = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
        
        while self.is_running:
            try:
                logger.info(f"Conectando a {ws_url} para Token ID: {config.TARGET_TOKEN_ID}")
                async with websockets.connect(ws_url) as ws:
                    # Payload de subcripción al Orderbook para un Asset específico
                    subscription_payload = {
                        "assets_ids": [config.TARGET_TOKEN_ID],
                        "type": "market"
                    }
                    await ws.send(json.dumps(subscription_payload))
                    logger.info("Suscripción enviada al WebSocket. Esperando mensajes...")
                    
                    # Loop de lectura continua
                    async for message in ws:
                        if not self.is_running:
                            break
                        
                        logger.info(f"Nuevo mensaje WS recibido: {message[:1000]}...") # Imprimir para depurar
                        data = json.loads(message)
                        
                        # Guardar Bids/Asks en memoria del Bot
                        if "bids" in data or "asks" in data:
                            if "bids" in data:
                                self.orderbook_data["bids"] = data["bids"]
                            if "asks" in data:
                                self.orderbook_data["asks"] = data["asks"]
                                    
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
