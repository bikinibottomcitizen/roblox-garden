"""
Main application class that orchestrates all components.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Set

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from roblox_garden.config.settings import Settings
from roblox_garden.models.shop import ShopItem, ShopData, ShopUpdate
from roblox_garden.filters.item_filters import RobloxGardenFilter
from roblox_garden.websocket.client import WebSocketClient
from roblox_garden.telegram.bot import TelegramBot
from roblox_garden.utils.formatters import MessageFormatter


class RobloxGardenApp:
    """Main application class."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.is_running = False
        
        # Core components
        self.websocket_client = WebSocketClient(settings)
        self.telegram_bot = TelegramBot(settings)
        self.message_formatter = MessageFormatter(settings)
        
        # Filters
        self.item_filter = RobloxGardenFilter.create_combined_filter()
        
        # State tracking
        self.current_shop_data: Optional[ShopData] = None
        self.last_full_update: Optional[datetime] = None
        self.known_items: Dict[str, ShopItem] = {}
        
        # Tasks
        self.websocket_task: Optional[asyncio.Task] = None
        self.scheduler_task: Optional[asyncio.Task] = None
    
    async def run(self) -> None:
        """Start the application."""
        logger.info("Starting Roblox Garden Parser application...")
        
        try:
            self.is_running = True
            
            # Initialize components
            await self.telegram_bot.initialize()
            
            # Send initial full report
            await self._send_initial_full_report()
            
            # Start background tasks
            self.websocket_task = asyncio.create_task(self._websocket_loop())
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            
            # Wait for tasks to complete
            await asyncio.gather(
                self.websocket_task,
                self.scheduler_task,
                return_exceptions=True
            )
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the application."""
        logger.info("Shutting down application...")
        
        self.is_running = False
        
        # Cancel tasks
        if self.websocket_task and not self.websocket_task.done():
            self.websocket_task.cancel()
            try:
                await self.websocket_task
            except asyncio.CancelledError:
                pass
        
        if self.scheduler_task and not self.scheduler_task.done():
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Shutdown components
        await self.websocket_client.close()
        await self.telegram_bot.shutdown()
        
        logger.info("Application shutdown complete")
    
    async def _websocket_loop(self) -> None:
        """Main WebSocket monitoring loop."""
        logger.info("Starting WebSocket monitoring loop...")
        
        while self.is_running:
            try:
                # Connect to WebSocket
                await self.websocket_client.connect()
                
                # Process incoming data
                async for shop_data in self.websocket_client.listen():
                    if not self.is_running:
                        break
                    
                    await self._process_shop_data(shop_data)
                
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                
                if self.is_running:
                    logger.info(f"Reconnecting in {self.settings.websocket_reconnect_delay} seconds...")
                    await asyncio.sleep(self.settings.websocket_reconnect_delay)
    
    async def _scheduler_loop(self) -> None:
        """Scheduler loop for periodic full updates."""
        logger.info("Starting scheduler loop...")
        
        while self.is_running:
            try:
                # Check if it's time for a full update
                now = datetime.now()
                
                if (self.last_full_update is None or 
                    now - self.last_full_update >= timedelta(seconds=self.settings.shop_update_interval)):
                    
                    await self._send_full_update()
                    self.last_full_update = now
                
                # Sleep for a short interval before checking again
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _process_shop_data(self, shop_data: ShopData) -> None:
        """Process new shop data and send updates."""
        logger.debug(f"Processing shop data with {len(shop_data.items)} items")
        
        # Filter items according to our rules
        filtered_items = shop_data.get_filtered_items(self.item_filter)
        
        # Update current shop data
        self.current_shop_data = shop_data
        
        # Detect new items
        new_items = self._detect_new_items(filtered_items)
        
        if new_items:
            logger.info(f"Detected {len(new_items)} new items")
            await self._send_new_items_update(new_items)
    
    def _detect_new_items(self, current_items: list[ShopItem]) -> list[ShopItem]:
        """Detect new items compared to known items."""
        new_items = []
        current_item_ids = {item.id for item in current_items}
        
        for item in current_items:
            if item.id not in self.known_items:
                new_items.append(item)
                self.known_items[item.id] = item
            elif item.in_stock and not self.known_items[item.id].in_stock:
                # Item came back in stock
                new_items.append(item)
                self.known_items[item.id] = item
        
        # Clean up items that are no longer available
        self.known_items = {
            item_id: item for item_id, item in self.known_items.items()
            if item_id in current_item_ids
        }
        
        return new_items
    
    async def _send_new_items_update(self, new_items: list[ShopItem]) -> None:
        """Send update about new items to the updates channel."""
        if not new_items:
            return
        
        try:
            # Format message for new items
            message = self.message_formatter.format_new_items_message(new_items)
            
            # Send to updates channel
            success = await self.telegram_bot.send_to_updates_channel(message)
            
            if success:
                logger.info(f"Sent new items update for {len(new_items)} items")
            else:
                logger.error("Failed to send new items update")
            
        except Exception as e:
            logger.error(f"Failed to send new items update: {e}")
    
    async def _send_full_update(self) -> None:
        """Send full shop report to the full channel."""
        if not self.current_shop_data:
            logger.warning("No shop data available for full update")
            return
        
        try:
            # Filter items for full report
            filtered_items = self.current_shop_data.get_filtered_items(self.item_filter)
            
            if not filtered_items:
                logger.info("No items to include in full update")
                return
            
            # Format full report message
            message = self.message_formatter.format_full_report_message(
                filtered_items,
                self.current_shop_data.timestamp
            )
            
            # Send to full channel
            success = await self.telegram_bot.send_to_full_channel(message)
            
            if success:
                logger.info(f"Sent full update with {len(filtered_items)} items")
            else:
                logger.error("Failed to send full update")
            
        except Exception as e:
            logger.error(f"Failed to send full update: {e}")

    async def _send_initial_full_report(self) -> None:
        """Send initial full report immediately after startup."""
        try:
            logger.info("Sending initial full report...")
            
            # Get initial shop data
            shop_data = await self.websocket_client.fetch_shop_data()
            
            if not shop_data:
                logger.warning("No shop data available for initial report")
                return
            
            # Set current shop data
            self.current_shop_data = shop_data
            
            # Filter items for initial report
            filtered_items = shop_data.get_filtered_items(self.item_filter)
            
            if not filtered_items:
                logger.info("No items to include in initial report")
                # Send empty report
                message = self.message_formatter.format_full_report_message([], shop_data.timestamp)
            else:
                # Format full report message
                message = self.message_formatter.format_full_report_message(
                    filtered_items,
                    shop_data.timestamp
                )
                
                # Initialize known items
                for item in filtered_items:
                    self.known_items[item.id] = item
            
            # Send to full channel
            success = await self.telegram_bot.send_to_full_channel(message)
            
            if success:
                logger.info(f"Initial full report sent with {len(filtered_items)} items")
                self.last_full_update = datetime.now()
            else:
                logger.error("Failed to send initial full report")
                
        except Exception as e:
            logger.error(f"Failed to send initial full report: {e}")
