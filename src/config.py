import os
from dotenv import load_dotenv

# Cargar .env explícitamente desde la carpeta superior
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class Config:
    def __init__(self):
        self.HOST = self._get_env("POLYMARKET_HOST", "https://clob.polymarket.com")
        self.CHAIN_ID = int(self._get_env("POLYMARKET_CHAIN_ID", 137))
        self.PRIVATE_KEY = self._get_env("PRIVATE_KEY", secure=True)
        self.FUNDER_ADDRESS = self._get_env("FUNDER_ADDRESS")
        self.CAPITAL_INICIAL = float(self._get_env("CAPITAL_INICIAL", 10.0))
        
        # Límite Max Kelly (Ajustado) - Arriesga máximo el 5% del capital sugerido por de Kelly
        self.KELLY_FRACTION_MODIFIER = 0.05 

    def _get_env(self, key: str, default: str = None, secure: bool = False) -> str:
        val = os.getenv(key, default)
        if val is None:
            raise ValueError(f"Falta variable de entorno requerida: {key}")
        return val

config = Config()
