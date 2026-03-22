import json
import os
import time
import logging
import config
from src.notifier import AlertNotifier

logger = logging.getLogger(__name__)

class MarketMonitor:
    def __init__(self, client):
        self.client = client
        self.notifier = AlertNotifier()
        self.state_file = "data/prices_state.json"
        self.threshold = config.VOLATILITY_THRESHOLD
        self.prices = self._load_state()

    def _load_state(self):
        """Carga el historial de precios desde un JSON local (coste cero)."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error cargando estado: {e}")
        return {}

    def _save_state(self):
        """Guarda el estado actual en el JSON."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.prices, f, indent=4)
        except Exception as e:
            logger.error(f"Error guardando estado: {e}")

    def check_market(self, token_id, market_name="Desconocido"):
        """
        Consulta el precio actual y lo compara con el anterior.
        Lanza alerta si la volatilidad supera el umbral.
        """
        current_price = self.client.get_mid_price(token_id)
        
        if current_price is None:
            logger.warning(f"No se pudo obtener precio para {token_id}")
            return

        last_price = self.prices.get(token_id)

        if last_price is None:
            # Es la primera vez que vemos este mercado
            logger.info(f"Registrando precio inicial para {market_name}: ${current_price:.3f}")
            self.prices[token_id] = current_price
            self._save_state()
            return

        # Calcular cambio porcentual
        change_pct = (current_price - last_price) / last_price

        if abs(change_pct) >= self.threshold:
            # ¡Disparamos alerta!
            self.notifier.notify(market_name, last_price, current_price, change_pct)
            
            # Actualizamos el precio base para la siguiente alerta
            # Así evitamos recibir alertas infinitas si el precio se queda en el nuevo nivel
            self.prices[token_id] = current_price
            self._save_state()
        else:
            # Opcional: Log silencioso para saber que el bot está vivo
            print(f"[{market_name}] Precio estable: ${current_price:.3f} (Cambio: {change_pct:.2%})", end="\r")

    def run_loop(self, markets_to_watch):
        """
        Bucle infinito (para las 2-3 horas que lo uses).
        markets_to_watch: dict con {token_id: nombre_mercado}
        """
        print(f"{Colors.BLUE}--- MONITOR DE POLYNARKET ACTIVADO (Umbral: {self.threshold:.1%}) ---{Colors.ENDC}")
        print("Presiona Ctrl+C para detener el bot.\n")
        
        try:
            while True:
                for token_id, name in markets_to_watch.items():
                    self.check_market(token_id, name)
                
                # Esperamos según la configuración (ej: 5-15 minutos)
                # Convertimos minutos a segundos para el time.sleep()
                time.sleep(config.CHECK_INTERVAL_MINUTES * 60)
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Bot detenido por el usuario.{Colors.ENDC}")

# Añadir colores aquí también para el run_loop
class Colors:
    BLUE = '\033[94m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
