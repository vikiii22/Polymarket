"""Alert notifier for sending notifications via multiple channels."""

import requests
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class AlertNotifier:
    """
    Sends alerts through multiple channels (console, Telegram, etc.).
    """
    
    def __init__(
        self,
        telegram_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None
    ):
        """
        Initialize alert notifier.
        
        Args:
            telegram_token: Telegram bot token (optional)
            telegram_chat_id: Telegram chat ID (optional)
        """
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.telegram_enabled = bool(telegram_token and telegram_chat_id)
        
        if self.telegram_enabled:
            logger.info("Telegram notifications enabled")
        else:
            logger.info("Telegram notifications disabled (no credentials)")

    def _print_to_console(
        self,
        market_name: str,
        old_price: float,
        new_price: float,
        change_pct: float
    ) -> None:
        """
        Print alert to console with color formatting.
        
        Args:
            market_name: Name of the market
            old_price: Previous price
            new_price: Current price
            change_pct: Percentage change
        """
        color = Colors.GREEN if change_pct > 0 else Colors.FAIL
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print("\n" + "=" * 80)
        print(f"{Colors.BOLD}{Colors.HEADER}🚨 ALERTA DE VOLATILIDAD [{timestamp}]{Colors.ENDC}")
        print(f"{Colors.BOLD}MERCADO:{Colors.ENDC} {market_name}")
        print(
            f"{Colors.BOLD}PRECIO:{Colors.ENDC}  "
            f"${old_price:.3f} → {color}${new_price:.3f}{Colors.ENDC}"
        )
        print(f"{Colors.BOLD}CAMBIO:{Colors.ENDC}  {color}{change_pct:+.2%}{Colors.ENDC}")
        print("=" * 80 + "\n")

    def _send_to_telegram(
        self,
        market_name: str,
        old_price: float,
        new_price: float,
        change_pct: float
    ) -> bool:
        """
        Send alert to Telegram.
        
        Args:
            market_name: Name of the market
            old_price: Previous price
            new_price: Current price
            change_pct: Percentage change
            
        Returns:
            True if successful, False otherwise
        """
        if not self.telegram_enabled:
            return False

        emoji = "🚀" if change_pct > 0 else "⚠️"
        arrow = "↗️" if change_pct > 0 else "↘️"
        
        message = (
            f"{emoji} *ALERTA DE VOLATILIDAD* {arrow}\n\n"
            f"*Mercado:* {market_name}\n"
            f"*Precio Anterior:* ${old_price:.3f}\n"
            f"*Precio Actual:* ${new_price:.3f}\n"
            f"*Variación:* {change_pct:+.2%}\n"
        )
        
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, data=payload, timeout=5)
            response.raise_for_status()
            logger.info("Alert sent to Telegram successfully")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False

    def notify(
        self,
        market_name: str,
        old_price: float,
        new_price: float,
        change_pct: float
    ) -> None:
        """
        Send notification through all enabled channels.
        
        Args:
            market_name: Name of the market
            old_price: Previous price
            new_price: Current price
            change_pct: Percentage change
        """
        # Always show in console
        self._print_to_console(market_name, old_price, new_price, change_pct)
        
        # Send to Telegram if configured
        if self.telegram_enabled:
            self._send_to_telegram(market_name, old_price, new_price, change_pct)
