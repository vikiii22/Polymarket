"""
Polymarket Trading Bot - Professional Version 2.0
Main entry point for the trading bot.
"""

import logging
from typing import Dict

from tradingbot.config import config
from tradingbot.api.client import PolymarketClient
from tradingbot.market.monitor import MarketMonitor
from tradingbot.market.discovery import MarketDiscovery
from tradingbot.utils.logger import setup_logging


class Colors:
    """ANSI color codes for terminal output."""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_banner() -> None:
    """Print startup banner."""
    print(f"""
    {Colors.BLUE}{'='*80}{Colors.ENDC}
       {Colors.BOLD}🔥 POLYMARKET REAL-TIME MONITOR v2.0 🚀{Colors.ENDC}
       {Colors.YELLOW}Professional Architecture | Async Ready | Type-Safe{Colors.ENDC}
    {Colors.BLUE}{'='*80}{Colors.ENDC}
    """)


def main() -> None:
    """Main entry point for the trading bot."""
    # Setup logging first
    setup_logging(
        log_dir="logs",
        log_file="bot.log",
        level=logging.INFO,
        console_level=logging.WARNING  # Less noise in console
    )
    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info("Starting Polymarket Trading Bot v2.0")
    logger.info("="*80)
    
    # Print banner
    print_banner()
    
    # Show configuration
    print(f"📋 Configuración:")
    print(f"   • DRY_RUN:         {config.dry_run}")
    print(f"   • Umbral:          {config.volatility_threshold:.1%}")
    print(f"   • Intervalo:       {config.check_interval_seconds}s")
    print(f"   • Telegram:        {'✅ Habilitado' if config.telegram_token else '❌ Deshabilitado'}")
    print()
    
    try:
        # Initialize client
        logger.info("Initializing Polymarket client...")
        client = PolymarketClient(
            private_key=config.private_key,
            api_key=config.clob_api_key,
            api_secret=config.clob_api_secret,
            api_passphrase=config.clob_api_passphrase
        )
        print(f"{Colors.GREEN}✅ Cliente inicializado{Colors.ENDC}")
        
        # Discover trending markets
        logger.info("Discovering trending markets...")
        discovery = MarketDiscovery()
        print("\n🔎 Buscando mercados en tendencia...")
        trending_data = discovery.get_trending_markets(limit=15)
        
        if not trending_data:
            print(f"{Colors.YELLOW}⚠️  No se encontraron mercados en tendencia.{Colors.ENDC}")
            return
        
        # Validate liquidity
        print("📊 Validando liquidez en el libro de órdenes (CLOB)...")
        active_markets = []
        
        for m in trending_data:
            price = client.get_mid_price(m['id'])
            if price is not None:
                m['price'] = price
                active_markets.append(m)
                logger.debug(f"Market {m['name']}: price=${price:.3f}")
        
        # Add custom market if configured
        if config.target_token_id:
            logger.info(f"Adding custom target market: {config.target_token_id}")
            price = client.get_mid_price(config.target_token_id)
            if price is not None:
                active_markets.append({
                    "id": config.target_token_id,
                    "name": "⭐ Mercado Personalizado (.env)",
                    "volume": 0,
                    "price": price
                })
        
        if not active_markets:
            print(f"{Colors.YELLOW}⚠️  No hay mercados con liquidez disponible.{Colors.ENDC}")
            return
        
        # Display ranking
        discovery.print_ranking(active_markets)
        
        # Create markets dictionary for monitoring
        markets_to_watch: Dict[str, str] = {
            m['id']: m['name'] for m in active_markets
        }
        
        # Initialize monitor
        logger.info(f"Initializing monitor for {len(markets_to_watch)} markets")
        monitor = MarketMonitor(
            client=client,
            threshold=config.volatility_threshold,
            check_interval=config.check_interval_seconds
        )
        
        print(f"{Colors.GREEN}✅ Monitoreando {len(markets_to_watch)} mercados activos{Colors.ENDC}\n")
        
        # Start monitoring loop
        monitor.run_loop(markets_to_watch)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Bot detenido por el usuario{Colors.ENDC}")
        logger.info("Bot stopped by user (KeyboardInterrupt)")
    except Exception as e:
        print(f"\n{Colors.YELLOW}❌ Error crítico: {e}{Colors.ENDC}")
        logger.exception("Critical error in main loop")
        raise


if __name__ == "__main__":
    main()
