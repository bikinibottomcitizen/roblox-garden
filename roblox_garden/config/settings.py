"""
Application settings and configuration.
"""

from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Telegram Bot Configuration
    telegram_bot_token: str = Field(
        default="your_bot_token_here", 
        alias="TELEGRAM_BOT_TOKEN"
    )
    
    # Support both old and new channel ID variable names for backward compatibility
    telegram_full_channel_id: str = Field(
        default="your_full_channel_id", 
        alias="TELEGRAM_FULL_CHANNEL_ID"
    )
    telegram_updates_channel_id: str = Field(
        default="your_updates_channel_id", 
        alias="TELEGRAM_UPDATES_CHANNEL_ID"
    )
    
    # New Docker-compatible variable names (preferred)
    full_channel_id: Optional[str] = Field(default=None, alias="FULL_CHANNEL_ID")
    updates_channel_id: Optional[str] = Field(default=None, alias="UPDATES_CHANNEL_ID")
    
    # WebSocket Configuration
    ws_url: str = Field(
        default="wss://api.growagarden.com/socket",
        alias="WS_URL"
    )
    roblox_api_base_url: str = Field(
        default="https://gagapi.onrender.com",
        alias="ROBLOX_API_BASE_URL"
    )
    reconnect_delay: int = Field(default=5, alias="RECONNECT_DELAY")
    websocket_reconnect_delay: int = Field(default=5, alias="WEBSOCKET_RECONNECT_DELAY")
    max_reconnect_attempts: int = Field(default=10, alias="MAX_RECONNECT_ATTEMPTS")
    
    # Update intervals
    update_interval: int = Field(default=300, alias="UPDATE_INTERVAL")
    full_update_interval: int = Field(default=300, alias="FULL_UPDATE_INTERVAL")
    shop_update_interval: int = Field(default=300, alias="SHOP_UPDATE_INTERVAL")
    shop_check_interval: int = Field(default=30, alias="SHOP_CHECK_INTERVAL")
    
    # Report Configuration
    full_report_interval: int = Field(
        default=5, 
        alias="FULL_REPORT_INTERVAL",
        description="Interval in minutes for sending full reports (0:00, 0:05, 0:10, etc.)"
    )
    
    # Delay after stock update to ensure fresh data
    report_delay_after_stock_update: int = Field(
        default=30,
        alias="REPORT_DELAY_AFTER_STOCK_UPDATE",
        description="Seconds to wait after scheduled time to ensure data is updated"
    )
    
    # Timezone
    timezone: str = Field(default="Europe/Moscow", alias="TIMEZONE")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: Optional[str] = Field(default="logs/roblox_garden.log", alias="LOG_FILE")
    
    @property
    def effective_full_channel_id(self) -> str:
        """Get the effective full channel ID, preferring new variable name."""
        return self.full_channel_id or self.telegram_full_channel_id
    
    @property
    def effective_updates_channel_id(self) -> str:
        """Get the effective updates channel ID, preferring new variable name."""
        return self.updates_channel_id or self.telegram_updates_channel_id
    
    # Moscow timezone for timestamps
    timezone: str = Field(default="Europe/Moscow", alias="TIMEZONE")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }
