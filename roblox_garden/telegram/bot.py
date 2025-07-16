"""
Telegram bot for sending shop updates.
"""

import asyncio
from typing import Optional

try:
    from telegram import Bot
    from telegram.error import TelegramError
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    
    # Mock classes for development
    class TelegramError(Exception):
        pass
    
    class Bot:
        def __init__(self, token):
            self.token = token
        
        async def send_message(self, chat_id, text, parse_mode=None, disable_web_page_preview=True):
            logger.info(f"Mock send to {chat_id}: {text[:100]}...")

from roblox_garden.config.settings import Settings


class TelegramBot:
    """Telegram bot for sending shop updates."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.bot: Optional[Bot] = None
        self.is_initialized = False
    
    async def initialize(self) -> None:
        """Initialize the Telegram bot."""
        try:
            self.bot = Bot(token=self.settings.telegram_bot_token)
            
            # Test the bot by getting info
            try:
                me = await self.bot.get_me()
                logger.info(f"Telegram bot initialized: @{me.username}")
                self.is_initialized = True
            except Exception as e:
                logger.warning(f"Could not verify bot (using mock): {e}")
                self.is_initialized = True  # Allow mock mode
                
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            raise
    
    async def send_message(
        self,
        text: str,
        channel_id: str,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = True,
        max_retries: int = 3
    ) -> bool:
        """Send a message to a Telegram channel."""
        if not self.is_initialized or not self.bot:
            logger.error("Telegram bot not initialized")
            return False
        
        for attempt in range(max_retries):
            try:
                await self.bot.send_message(
                    chat_id=channel_id,
                    text=text,
                    parse_mode=parse_mode,
                    disable_web_page_preview=disable_web_page_preview
                )
                
                logger.debug(f"Message sent to {channel_id}")
                return True
                
            except TelegramError as e:
                logger.warning(f"Telegram error (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to send message after {max_retries} attempts")
                    return False
            
            except Exception as e:
                logger.error(f"Unexpected error sending message: {e}")
                return False
        
        return False
    
    async def send_to_updates_channel(self, text: str) -> bool:
        """Send message to the updates channel."""
        return await self.send_message(
            text=text,
            channel_id=self.settings.telegram_updates_channel_id
        )
    
    async def send_to_full_channel(self, text: str) -> bool:
        """Send message to the full reports channel."""
        return await self.send_message(
            text=text,
            channel_id=self.settings.telegram_full_channel_id
        )
    
    async def shutdown(self) -> None:
        """Shutdown the Telegram bot."""
        if self.bot:
            # No explicit cleanup needed for python-telegram-bot
            pass
        
        self.is_initialized = False
        logger.info("Telegram bot shutdown complete")
