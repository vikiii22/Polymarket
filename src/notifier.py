import requests
import logging
import config
from datetime import datetime

logger = logging.getLogger(__name__)

# Códigos de colores para la consola (ANSI)
# Explicación técnica: No necesitamos librerías como 'colorama' para cosas básicas, 
# usar códigos ANSI es estándar en Linux/Mac y modern terminals de Windows.
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class AlertNotifier:
    def __init__(self):
        self.token = config.TELEGRAM_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.telegram_enabled = bool(self.token and self.chat_id)

    def _print_to_console(self, market_name, old_price, new_price, change_pct):
        """Imprime una alerta visualmente atractiva en la consola."""
        color = Colors.GREEN if change_pct > 0 else Colors.FAIL
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print("\n" + "="*50)
        print(f"{Colors.BOLD}{Colors.HEADER}[ALERTA {timestamp}]{Colors.ENDC}")
        print(f"{Colors.BOLD}MERCADO:{Colors.ENDC} {market_name}")
        print(f"{Colors.BOLD}PRECIO:{Colors.ENDC}  ${old_price:.3f} -> {color}${new_price:.3f}{Colors.ENDC}")
        print(f"{Colors.BOLD}CAMBIO:{Colors.ENDC}  {color}{change_pct:+.2%}{Colors.ENDC}")
        print("="*50 + "\n")

    def _send_to_telegram(self, market_name, old_price, new_price, change_pct):
        """Envía la alerta a Telegram si está configurado."""
        if not self.telegram_enabled:
            return

        emoji = "🚀" if change_pct > 0 else "⚠️"
        message = (
            f"{emoji} *ALERTA DE VOLATILIDAD*\n\n"
            f"*Mercado:* {market_name}\n"
            f"*Precio Anterior:* ${old_price:.3f}\n"
            f"*Precio Actual:* ${new_price:.3f}\n"
            f"*Variación:* {change_pct:+.2%}\n"
        )
        
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        try:
            requests.post(url, data={"chat_id": self.chat_id, "text": message, "parse_mode": "Markdown"}, timeout=5)
        except Exception as e:
            logger.error(f"Error enviando a Telegram: {e}")

    def notify(self, market_name, old_price, new_price, change_pct):
        """Método principal que dispara todas las alertas activas."""
        # 1. Siempre avisar por consola
        self._print_to_console(market_name, old_price, new_price, change_pct)
        
        # 2. Avisar por Telegram si hay tokens (opcional)
        self._send_to_telegram(market_name, old_price, new_price, change_pct)
