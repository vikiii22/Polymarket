# Makefile for Polymarket Trading Bot

.PHONY: help install install-dev test format lint run run-dry clean

help:  ## Show this help message
	@echo "Polymarket Trading Bot - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package and dependencies
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -e ".[dev,async]"

test:  ## Run tests with coverage
	pytest tests/ -v --cov=tradingbot --cov-report=term-missing

format:  ## Format code with black and ruff
	black tradingbot/ tests/
	ruff check tradingbot/ tests/ --fix

lint:  ## Run linters (mypy, ruff)
	mypy tradingbot/
	ruff check tradingbot/ tests/
	black --check tradingbot/ tests/

run:  ## Run the trading bot
	python -m tradingbot.main

run-dry:  ## Run in DRY_RUN mode
	DRY_RUN=true python -m tradingbot.main

clean:  ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

logs:  ## View recent bot logs
	tail -f logs/bot.log

check:  ## Run all checks (format, lint, test)
	@make format
	@make lint
	@make test
	@echo "\n✅ All checks passed!"
