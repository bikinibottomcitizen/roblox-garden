"""
Application settings and configuration.
"""

from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Telegram Bot Configuration
    telegram_bot_token: str = Field(default="your_bot_token_here", alias="TELEGRAM_BOT_TOKEN")
    telegram_full_channel_id: str = Field(default="your_full_channel_id", alias="TELEGRAM_FULL_CHANNEL_ID")
    telegram_updates_channel_id: str = Field(default="your_updates_channel_id", alias="TELEGRAM_UPDATES_CHANNEL_ID")
    
    # WebSocket Configuration
    roblox_api_base_url: str = Field(
        default="https://gagapi.onrender.com",
        alias="ROBLOX_API_BASE_URL"
    )
    websocket_reconnect_delay: int = Field(default=5, alias="WEBSOCKET_RECONNECT_DELAY")
    shop_update_interval: int = Field(default=300, alias="SHOP_UPDATE_INTERVAL")  # 5 minutes
    
    # Logging Configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: Optional[str] = Field(default="logs/roblox_garden.log", alias="LOG_FILE")
    
    # Moscow timezone for timestamps
    timezone: str = Field(default="Europe/Moscow", alias="TIMEZONE")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }
