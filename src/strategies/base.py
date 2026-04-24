from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    @abstractmethod
    async def evaluate(self):
        """Evalúa las condiciones del mercado y ejecuta operaciones si es necesario."""
        pass
