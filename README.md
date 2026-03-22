# 🚀 Polymarket Trading Bot v2.0 - Professional Edition

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Polymarket](https://img.shields.io/badge/Polymarket-CLOB-purple.svg?style=for-the-badge&logo=polygon&logoColor=white)](https://polymarket.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Type Checked](https://img.shields.io/badge/Type_Checked-Pydantic-success.svg?style=for-the-badge)](https://docs.pydantic.dev/)

> **🔥 Professional trading bot for Polymarket with real-time monitoring, type-safe configuration, and production-ready architecture.**

---

## 🆕 What's New in v2.0

### ⚡ Real-Time Monitoring (120x Faster)
- **Before**: Polling every 10 minutes (600 seconds)
- **Now**: Updates every 5 seconds (configurable down to 1s)
- **Result**: Catch price movements 120x faster

### 🏗️ Professional Architecture
```
tradingbot/
├── api/          # API client with retry logic & type hints
├── market/       # Discovery & monitoring modules
├── strategies/   # Extensible strategy framework
├── notifications/# Multi-channel alerts (Console, Telegram)
└── utils/        # Validators, logging, decorators
```

### 🛡️ Type-Safe Configuration
- **Pydantic BaseSettings** with automatic validation
- Invalid keys auto-detected with clear error messages
- DRY_RUN automatically enabled for safety

### 📊 Professional Logging
- Rotating file logs (`logs/bot.log` with 10MB rotation)
- Structured logging with timestamps and levels
- Separate console and file log levels

### 🔧 Developer Experience
- `pyproject.toml` for modern Python packaging
- `Makefile` with common commands
- Type hints throughout codebase
- Ready for `pytest`, `mypy`, `black`, `ruff`

---

## 📈 Key Features

- **✅ Automated Market Monitoring**: Near real-time price tracking (5s intervals)
- **🛡️ Smart Key Validation**: Detects invalid PRIVATE_KEY formats (e.g., UUID with hyphens)
- **🧪 Dry Run Mode**: Safe simulation without risking real funds
- **📈 Performance Logging**: Detailed tracking in `logs/bot.log` and `logs/balance_history.txt`
- **⚡ Retry Logic**: Automatic retries with exponential backoff for API failures
- **🔧 Highly Configurable**: All settings via `.env` with validation

---

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.10+**
- Polymarket account (optional for read-only mode)

### Quick Start

1. **Clone and Install**
   ```bash
   git clone https://github.com/tu-usuario/polymarket-bot.git
   cd polymarket-bot
   pip install -e .
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run the Bot**
   ```bash
   # Using Python module
   python -m tradingbot.main
   
   # Using Makefile
   make run
   
   # Force dry-run mode
   make run-dry
   ```

---

## ⚙️ Configuration

### Basic Setup (Monitoring Only)

```env
# .env file
DRY_RUN=True
CHECK_INTERVAL_SECONDS=5
VOLATILITY_THRESHOLD=0.05
```

### With Telegram Alerts

```env
TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=12345678
```

### Live Trading (⚠️ Use with Caution)

```env
# Must be 64 hexadecimal characters (no hyphens!)
PRIVATE_KEY=a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890
DRY_RUN=False
```

**Common Error Fix:**
```
❌ Error: "Non-hexadecimal digit found"
✅ Solution: Your PRIVATE_KEY has invalid format (probably UUID with hyphens).
           Must be 64 pure hex characters: 0-9, a-f, A-F only.
```

---

## 🚀 Usage

### Using Makefile (Recommended)

```bash
make install       # Install dependencies
make run           # Run bot
make run-dry       # Run in simulation mode
make test          # Run tests
make format        # Format code
make lint          # Check code quality
make logs          # View live logs
```

### Direct Python Commands

```bash
# Run bot
python -m tradingbot.main

# Run tests (when implemented)
pytest tests/ -v --cov=tradingbot

# Format code
black tradingbot/ tests/
ruff check tradingbot/ --fix

# Type checking
mypy tradingbot/
```

---

## 📊 Real-Time Performance Comparison

### Before v2.0 (Polling)
```
[10:00:00] Check markets...
[10:10:00] Check markets...  ← 10 minutes gap
[10:20:00] Check markets...
```
**Missing**: All price movements in 10-minute windows

### After v2.0 (Real-Time)
```
[10:00:00] Check markets...
[10:00:05] Check markets...  ← 5 seconds gap
[10:00:10] Check markets...
[10:00:15] Check markets...
```
**Catching**: Price movements within seconds

---

## 🏗️ Project Structure

```
polymarket-bot/
├── tradingbot/              # Main package
│   ├── __init__.py
│   ├── main.py             # Entry point
│   ├── config.py           # Pydantic configuration
│   │
│   ├── api/                # API client layer
│   │   ├── client.py       # Enhanced CLOB client
│   │   ├── models.py       # Data models (OrderBook, Balance, etc.)
│   │   └── exceptions.py   # Custom exceptions
│   │
│   ├── market/             # Market data modules
│   │   ├── discovery.py    # Trending market discovery
│   │   ├── monitor.py      # Real-time price monitoring
│   │   ├── models.py       # Market data classes
│   │   └── events.py       # Event system
│   │
│   ├── strategies/         # Trading strategies
│   │   ├── base.py         # Abstract strategy class
│   │   └── market_maker.py # Market making implementation
│   │
│   ├── notifications/      # Alert system
│   │   └── notifier.py     # Multi-channel notifier
│   │
│   └── utils/              # Utilities
│       ├── validators.py   # Input validation
│       ├── logger.py       # Logging configuration
│       └── decorators.py   # Retry, timeout decorators
│
├── logs/                   # Generated logs
│   ├── bot.log            # Main application log
│   └── balance_history.txt
│
├── tests/                  # Test suite (to be implemented)
│   ├── unit/
│   └── integration/
│
├── pyproject.toml         # Modern Python packaging
├── Makefile               # Development commands
├── .env                   # Your configuration (not committed)
├── .env.example           # Configuration template
└── README.md              # This file
```

---

## 🔍 Troubleshooting

### Error: "Non-hexadecimal digit found"

**Cause**: Your `PRIVATE_KEY` in `.env` has invalid format (likely a UUID with hyphens)

**Solution**:
```env
# ❌ WRONG (UUID format)
PRIVATE_KEY=019d084e-0940-781f-8173-5b22bd33da09

# ✅ CORRECT (64 hex characters)
PRIVATE_KEY=a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890
# or with 0x prefix
PRIVATE_KEY=0xa1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890
```

The bot will now auto-detect this and force DRY_RUN mode for safety.

### Error: "Module 'tradingbot' has no attribute..."

**Cause**: Running from wrong directory or missing `__init__.py` files

**Solution**:
```bash
# Run from project root directory
cd /path/to/polymarket-bot
python -m tradingbot.main
```

### No Markets Found

**Cause**: Network issues or Polymarket API temporarily down

**Solution**:
1. Check internet connection
2. Review `logs/bot.log` for specific errors
3. Try increasing `CHECK_INTERVAL_SECONDS` to reduce API pressure

---

## 🧪 Testing (Coming Soon)

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run unit tests
pytest tests/unit/ -v

# Run with coverage
pytest --cov=tradingbot --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## 📚 Documentation

- **Architecture**: See `docs/architecture.md` (to be created)
- **API Reference**: See `docs/api_reference.md` (to be created)
- **Strategy Development**: See `docs/strategies.md` (to be created)

---

## ⚠️ Disclaimer

Este bot es una herramienta educativa y de trading experimental. El trading de criptoactivos conlleva un alto riesgo. **No inviertas dinero que no puedas permitirte perder.** El autor no se hace responsable de pérdidas financieras derivadas del uso de este software.

---

<p align="center">
  Hecho con ❤️ para la comunidad de Polymarket 🚀
</p>
