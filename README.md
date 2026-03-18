# 🚀 Polymarket Market Maker Bot

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Polymarket](https://img.shields.io/badge/Polymarket-CLOB-purple.svg?style=for-the-badge&logo=polygon&logoColor=white)](https://polymarket.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Status-Active-green.svg?style=for-the-badge)](https://github.com/josev/polymarket-bot)

> **Un bot de trading automatizado para Polymarket que utiliza una estrategia de Market Making con gestión de inventario y simulación en tiempo real.**

---

## 📸 Overview

Este proyectico está diseñado para proveer liquidez en mercados específicos de Polymarket (CLOB). El bot calcula el **Mid-Price** dinámicamente y coloca órdenes de compra (Bids) y venta (Asks) alrededor de él, ajustando su posición para minimizar riesgos.

![Polymarket Trading](https://images.mirror-media.xyz/publication-images/7d_zG5hH_Jq9K0o9Y_3z9.png?height=600&width=1200)

---

## 🔥 Key Features

- **✅ Automated Market Making**: Colocación automática de órdenes limitadas.
- **🛡️ Inventory Management (Skewing)**: Si el bot tiene muchas acciones, baja los precios de compra y de venta para incentivar la salida de la posición.
- **🧪 Dry Run Mode**: Simulación completa sin usar fondos reales. Prueba tu estrategia antes de ir en vivo.
- **📈 Performance Logging**: Seguimiento detallado del valor del portafolio, cash y shares en `balance_history.txt`.
- **⚡ Safety First**: Cancelación automática de todas las órdenes al detener el bot (Ctrl+C).
- **🔧 Highly Configurable**: Ajusta el spread, tamaño de orden y exposición máxima desde un simple `.env`.

---

## 📈 Trading Strategy

El bot utiliza una lógica de **Mid-Price Spreading**:

1.  **Calcula el Mid-Price**: `(Best Bid + Best Ask) / 2`.
2.  **Define el Spread**: Aplica un spread porcentual (ej. 2%) alrededor del mid-price.
3.  **Ajuste por Riesgo**: Si el inventario supera el 70% de la capacidad máxima (`MAX_POSITION`), el bot entra en modo **"Skewing"**:
    - Baja el Bid para dejar de comprar caro.
    - Baja el Ask para vender más rápido y reducir exposición.

---

## 🛠️ Installation & Setup

### 1. Requisitos
- Python 3.8+
- Una cuenta en Polymarket (API Keys opcionales para Dry Run).

### 2. Clonar y Preparar
```bash
git clone https://github.com/tu-usuario/polymarket-bot.git
cd polymarket-bot
pip install -r requirements.txt
```

### 3. Configuración (`.env`)
Copia el archivo de ejemplo y rellena tus datos:
```bash
cp .env.example .env
```

**Variables clave:**
- `PRIVATE_KEY`: Tu clave privada de Polygon (necesaria para trading real).
- `TARGET_TOKEN_ID`: El ID del mercado en el que quieres operar.
- `DRY_RUN`: Ponlo en `True` para simular, `False` para dinero real 🤑.

---

## 📊 Performance & Stats

El bot genera logs automáticos de su rendimiento en `balance_history.txt`:

```text
[2026-03-18 14:00:00] Cash: $10.50 | Shares: 5.00 | Portfolio Val: $13.00 | Mid-Price: 0.500
[2026-03-18 14:05:00] Cash: $8.20  | Shares: 10.00 | Portfolio Val: $13.20 | Mid-Price: 0.500
```

Puedes ver tu posición actual en tiempo real en `current_position.json`.

---

## 🚀 Usage

Para lanzar el bot, simplemente ejecuta:

```bash
python main.py
```

*Si estás en modo **Live**, el bot esperará 5 segundos antes de empezar para que puedas cancelar por seguridad.*

---

## ⚠️ Disclaimer

Este bot es una herramienta educativa y de trading experimental. El trading de criptoactivos conlleva un alto riesgo. **No inviertas dinero que no puedas permitirte perder.** El autor no se hace responsable de pérdidas financieras derivadas del uso de este software.

---

<p align="center">
  Hecho con ❤️ para la comunidad de Polymarket 🚀
</p>
