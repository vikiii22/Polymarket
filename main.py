import logging
import config
from client import PolymarketClient
from src.monitor import MarketMonitor
from src.discovery import MarketDiscovery

# Logs mínimos y claros
logging.basicConfig(level=logging.WARNING, format='%(message)s')
logger = logging.getLogger(__name__)

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    ENDC = '\033[0m'

def main():
    print(f"""
    {Colors.BLUE}==========================================={Colors.ENDC}
       🔥 POLYMARKET REAL-TIME MONITOR 🚀
    {Colors.BLUE}==========================================={Colors.ENDC}
    """)

    try:
        client = PolymarketClient()
        discovery = MarketDiscovery()

        print("🔎 Buscando mercados en tendencia...")
        trending_data = discovery.get_trending_markets(limit=15)
        
        # 1. FILTRADO INTELIGENTE: Solo monitoreamos lo que tiene liquidez real
        print("📊 Validando liquidez en el libro de órdenes (CLOB)...")
        active_markets = []
        
        for m in trending_data:
            price = client.get_mid_price(m['id'])
            if price:
                m['price'] = price
                active_markets.append(m)

        if config.TARGET_TOKEN_ID:
            price = client.get_mid_price(config.TARGET_TOKEN_ID)
            if price:
                active_markets.append({
                    "id": config.TARGET_TOKEN_ID,
                    "name": "⭐ Mercado Personalizado (.env)",
                    "volume": 0,
                    "price": price
                })

        if not active_markets:
            print("⚠️ No se encontraron mercados con liquidez en el CLOB en este momento.")
            return

        # 2. Mostrar Ranking Limpio
        discovery.print_ranking(active_markets)

        # 3. Lanzar Monitor
        markets_to_watch = {m['id']: m['name'] for m in active_markets}
        monitor = MarketMonitor(client)
        
        print(f"{Colors.GREEN}✅ Monitoreando {len(markets_to_watch)} mercados activos.{Colors.ENDC}")
        monitor.run_loop(markets_to_watch)

    except KeyboardInterrupt:
        print("\n👋 Bot detenido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")

if __name__ == "__main__":
    main()
