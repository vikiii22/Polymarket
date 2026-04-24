class RiskManager:
    def __init__(self, current_capital: float, kelly_modifier: float = 0.05):
        self.capital = current_capital
        self.modifier = kelly_modifier

    def calculate_position_size(self, win_probability: float, odds_received: float) -> float:
        """
        Calcula el tamaño de posición usando fórmula Kelly invertida para exchanges
        Kelly % = W - [(1 - W) / R]
        W = Probabilidad de ganar (0.0 a 1.0)
        R = Ratio de recompensa (Beneficio neto esperado / Pérdida esperada)
        """
        # Evitar división por cero
        if odds_received <= 0: return 0.0
        
        q = 1.0 - win_probability
        
        kelly_percentage = win_probability - (q / odds_received)
        if kelly_percentage <= 0:
            return 0.0 # No operar, ventaja negativa
            
        # Aplicamos el Fraccionario (Para $10, limitaría a centavos para sobrevivir la varianza)
        safe_percentage = kelly_percentage * self.modifier
        position_size = self.capital * safe_percentage
        
        return position_size
