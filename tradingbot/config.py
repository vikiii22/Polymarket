"""Configuration management using Pydantic for validation."""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

# Try to import validators
try:
    from tradingbot.utils.validators import validate_private_key
except ImportError:
    def validate_private_key(key):
        return (bool(key), "")


class TradingConfig(BaseSettings):
    """
    Trading bot configuration with automatic validation.
    
    All settings are loaded from environment variables (.env file).
    Pydantic automatically validates types and constraints.
    """
    
    # ===== API Configuration =====
    private_key: Optional[str] = Field(
        default=None,
        description="Ethereum private key (64 hex characters)"
    )
    clob_api_key: Optional[str] = Field(default=None, alias="CLOB_API_KEY")
    clob_api_secret: Optional[str] = Field(default=None, alias="CLOB_API_SECRET")
    clob_api_passphrase: Optional[str] = Field(default=None, alias="CLOB_API_PASSPHRASE")
    
    # ===== Trading Parameters =====
    target_token_id: Optional[str] = Field(default=None, alias="TARGET_TOKEN_ID")
    dry_run: bool = Field(default=True, alias="DRY_RUN")
    
    # ===== Telegram Configuration =====
    telegram_token: Optional[str] = Field(default=None, alias="TELEGRAM_TOKEN")
    telegram_chat_id: Optional[str] = Field(default=None, alias="TELEGRAM_CHAT_ID")
    
    # ===== Alert Parameters =====
    volatility_threshold: float = Field(
        default=0.05,
        ge=0.001,
        le=1.0,
        description="Volatility threshold (0.001 to 1.0)"
    )
    check_interval_seconds: int = Field(
        default=5,
        ge=1,
        le=3600,
        alias="CHECK_INTERVAL_SECONDS",
        description="Seconds between price checks (1 to 3600)"
    )
    
    # Support old CHECK_INTERVAL_MINUTES for backward compatibility
    check_interval_minutes: Optional[int] = Field(
        default=None,
        ge=1,
        le=60,
        alias="CHECK_INTERVAL_MINUTES",
        description="DEPRECATED: Use CHECK_INTERVAL_SECONDS instead"
    )
    
    # ===== Strategy Defaults =====
    spread: float = Field(default=0.02, ge=0.001, le=0.5)
    min_spread: float = Field(default=0.005, ge=0.0001, le=0.1)
    order_size: float = Field(default=10.0, ge=1.0, le=10000.0)
    max_position: float = Field(default=50.0, ge=1.0, le=100000.0)
    sleep_interval: int = Field(default=5, ge=1, le=60)
    
    # ===== Simulation/Performance Tracking =====
    initial_balance: float = Field(default=10.0, ge=1.0)
    balance_log_file: str = Field(default="logs/balance_history.txt")
    position_file: str = Field(default="data/current_position.json")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env
    
    @field_validator("private_key")
    @classmethod
    def validate_private_key_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate private key format using custom validator."""
        if v:
            is_valid, message = validate_private_key(v)
            if not is_valid:
                print(f"⚠️  WARNING: {message}")
                print("    Your PRIVATE_KEY format is invalid. It must be 64 hexadecimal characters.")
                print("    Example: 'a1b2c3d4e5f67890...' (64 chars) or '0xa1b2c3d4...' (66 with 0x)")
                print("    🔒 Forcing DRY_RUN mode for safety.")
                return None  # Invalid key is cleared
        return v
    
    @field_validator("check_interval_seconds")
    @classmethod
    def handle_minutes_fallback(cls, v: int, info) -> int:
        """Handle backward compatibility with CHECK_INTERVAL_MINUTES."""
        # If CHECK_INTERVAL_MINUTES is set, convert to seconds
        if hasattr(info, 'data') and info.data.get('check_interval_minutes'):
            minutes = info.data['check_interval_minutes']
            return minutes * 60
        return v
    
    def model_post_init(self, __context) -> None:
        """Post-initialization validation and warnings."""
        # Force DRY_RUN if no valid private key
        if not self.private_key:
            if not self.dry_run:
                print("⚠️  WARNING: No valid PRIVATE_KEY found. Forcing DRY_RUN mode.")
            object.__setattr__(self, 'dry_run', True)
        
        # Create necessary directories
        Path(self.balance_log_file).parent.mkdir(parents=True, exist_ok=True)
        Path(self.position_file).parent.mkdir(parents=True, exist_ok=True)


# Create global config instance
# This will load and validate settings from .env on import
try:
    config = TradingConfig()
except Exception as e:
    print(f"❌ Error loading configuration: {e}")
    print("   Using default values for all settings.")
    print("   Make sure your .env file is properly formatted.")
    # Create config with defaults
    config = TradingConfig(_env_file=None)
