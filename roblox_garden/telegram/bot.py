"""
Telegram bot integration using aiogram for sending shop updates.
"""
import asyncio
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramNetworkError
from loguru import logger

from ..config.settings import Settings


class TelegramBot:
    """Telegram bot for sending shop updates to channels."""
    
    def __init__(self, settings: Settings):
        """Initialize the Telegram bot."""
        self.settings = settings
        self.bot: Optional[Bot] = None
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """Initialize the Telegram bot connection."""
        try:
            # Check if token is available
            if not self.settings.telegram_bot_token:
                logger.error("Telegram bot token not configured")
                raise ValueError("Telegram bot token is required")
            
            # Initialize the bot
            self.bot = Bot(token=self.settings.telegram_bot_token)
            
            # Test the bot by getting info
            try:
                me = await self.bot.get_me()
                logger.info(f"Telegram bot initialized successfully: @{me.username}")
                self.is_initialized = True
            except TelegramAPIError as e:
                logger.error(f"Failed to verify bot token: {e}")
                raise
                
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
        """Send a message to a Telegram channel with retry logic."""
        if not self.is_initialized or not self.bot:
            logger.error("Telegram bot not initialized")
            return False
        
        # Validate channel ID
        if not channel_id:
            logger.error("Channel ID not provided")
            return False
        
        for attempt in range(max_retries):
            try:
                await self.bot.send_message(
                    chat_id=channel_id,
                    text=text,
                    parse_mode=parse_mode,
                    disable_web_page_preview=disable_web_page_preview
                )
                
                logger.debug(f"Message sent to channel {channel_id}")
                return True
                
            except TelegramBadRequest as e:
                logger.warning(f"Bad request to Telegram API (attempt {attempt + 1}/{max_retries}): {e}")
                
                # Don't retry for bad requests (invalid channel, permissions, etc.)
                if "chat not found" in str(e).lower() or "forbidden" in str(e).lower():
                    logger.error(f"Cannot send to channel {channel_id}: {e}")
                    return False
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to send message after {max_retries} attempts: {e}")
                    return False
                    
            except TelegramNetworkError as e:
                logger.warning(f"Network error (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Network failed after {max_retries} attempts: {e}")
                    return False
                    
            except TelegramAPIError as e:
                logger.warning(f"Telegram API error (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"API error after {max_retries} attempts: {e}")
                    return False
            
            except Exception as e:
                logger.error(f"Unexpected error sending message: {e}")
                return False
        
        return False
    
    async def send_to_updates_channel(self, text: str) -> bool:
        """Send message to the real-time updates channel."""
        if not self.settings.telegram_updates_channel_id:
            logger.error("Updates channel ID not configured")
            return False
            
        return await self.send_message(
            text=text,
            channel_id=self.settings.telegram_updates_channel_id,
            parse_mode="Markdown"
        )
    
    async def send_to_full_channel(self, text: str) -> bool:
        """Send message to the full reports channel."""
        if not self.settings.telegram_full_channel_id:
            logger.error("Full reports channel ID not configured")
            return False
            
        return await self.send_message(
            text=text,
            channel_id=self.settings.telegram_full_channel_id,
            parse_mode="Markdown"
        )
    
    async def test_connection(self) -> bool:
        """Test if the bot can send messages to configured channels."""
        if not self.is_initialized:
            logger.error("Bot not initialized")
            return False
        
        test_message = "🤖 Тест подключения бота Roblox Garden"
        
        # Test updates channel
        updates_success = await self.send_to_updates_channel(test_message)
        if updates_success:
            logger.info("✅ Updates channel test successful")
        else:
            logger.error("❌ Updates channel test failed")
        
        # Test full reports channel  
        full_success = await self.send_to_full_channel(test_message)
        if full_success:
            logger.info("✅ Full reports channel test successful")
        else:
            logger.error("❌ Full reports channel test failed")
        
        return updates_success and full_success
    
    async def shutdown(self) -> None:
        """Shutdown the Telegram bot and close session."""
        if self.bot:
            try:
                await self.bot.session.close()
                logger.info("Telegram bot session closed")
            except Exception as e:
                logger.warning(f"Error closing bot session: {e}")
        
        self.bot = None
        self.is_initialized = False
        logger.info("Telegram bot shutdown complete")
