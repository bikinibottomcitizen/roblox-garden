"""
Main application class that orchestrates all components.
"""

import asyncio
import signal
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
        self.known_items: Dict[str, ShopItem] = {}
        
        # Tasks
        self.websocket_task: Optional[asyncio.Task] = None
        self.scheduler_task: Optional[asyncio.Task] = None
        
        # Signal handling
        self._shutdown_event = asyncio.Event()
    
    async def run(self) -> None:
        """Start the application."""
        logger.info("Starting Roblox Garden Parser application...")
        
        try:
            self.is_running = True
            
            # Setup signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            # Initialize components
            await self.telegram_bot.initialize()
            
            # Send initial full report
            await self._send_initial_full_report()
            
            # Start background tasks
            self.websocket_task = asyncio.create_task(self._websocket_loop())
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            
            logger.info("🚀 Application started successfully! Press Ctrl+C to stop.")
            
            # Wait for shutdown signal or task completion
            tasks_to_wait = [
                asyncio.create_task(self._shutdown_event.wait()),
                self.websocket_task,
                self.scheduler_task
            ]
            
            done, pending = await asyncio.wait(
                tasks_to_wait,
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt (Ctrl+C)")
        except Exception as e:
            logger.error(f"Application error: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the application."""
        logger.info("🛑 Shutting down application...")
        
        self.is_running = False
        
        # Cancel tasks
        tasks_to_cancel = []
        if self.websocket_task and not self.websocket_task.done():
            tasks_to_cancel.append(("WebSocket", self.websocket_task))
        if self.scheduler_task and not self.scheduler_task.done():
            tasks_to_cancel.append(("Scheduler", self.scheduler_task))
        
        for task_name, task in tasks_to_cancel:
            logger.info(f"🔄 Cancelling {task_name} task...")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"✅ {task_name} task cancelled")
            except Exception as e:
                logger.error(f"❌ Error cancelling {task_name} task: {e}")
        
        # Shutdown components
        logger.info("🔌 Closing connections...")
        await self.websocket_client.close()
        await self.telegram_bot.shutdown()
        
        logger.info("✅ Application shutdown complete")
        logger.info("👋 Goodbye!")
    
    async def _websocket_loop(self) -> None:
        """Main WebSocket monitoring loop with robust error handling."""
        logger.info("Starting WebSocket monitoring loop...")
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.is_running and not self._shutdown_event.is_set():
            try:
                consecutive_errors = 0  # Reset on successful iteration
                
                # Connect to WebSocket
                await self.websocket_client.connect()
                
                # Process incoming data
                async for shop_data in self.websocket_client.listen():
                    if not self.is_running or self._shutdown_event.is_set():
                        break
                    
                    await self._process_shop_data(shop_data)
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"WebSocket error (attempt {consecutive_errors}): {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.error(f"Too many consecutive errors ({max_consecutive_errors}), stopping")
                    break
                
                if self.is_running and not self._shutdown_event.is_set():
                    wait_time = min(self.settings.websocket_reconnect_delay * consecutive_errors, 60)
                    logger.info(f"Reconnecting in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
        
        logger.info("WebSocket monitoring loop ended")
    
    async def _scheduler_loop(self) -> None:
        """Scheduler loop for periodic full updates at exact time intervals."""
        logger.info(f"Starting scheduler loop (full reports every {self.settings.full_report_interval} minutes at :00, :05, :10, etc.)")
        
        while self.is_running and not self._shutdown_event.is_set():
            try:
                # Calculate next scheduled time (every N minutes at :00, :05, :10, etc.)
                now = datetime.now()
                current_minute = now.minute
                interval = self.settings.full_report_interval
                
                # Calculate next target minute
                next_minute = ((current_minute // interval) + 1) * interval
                if next_minute >= 60:
                    next_minute = 0
                    next_time = now.replace(hour=(now.hour + 1) % 24, minute=next_minute, second=0, microsecond=0)
                else:
                    next_time = now.replace(minute=next_minute, second=0, microsecond=0)
                
                # If we're past the target time, move to next interval
                if next_time <= now:
                    next_minute = ((next_minute // interval) + 1) * interval
                    if next_minute >= 60:
                        next_minute = 0
                        next_time = next_time.replace(hour=(next_time.hour + 1) % 24, minute=next_minute)
                    else:
                        next_time = next_time.replace(minute=next_minute)
                
                # Calculate sleep time
                sleep_seconds = (next_time - now).total_seconds()
                
                logger.info(f"Next full report scheduled at {next_time.strftime('%H:%M:%S')} (in {sleep_seconds:.1f} seconds)")
                
                # Sleep until next scheduled time
                await asyncio.sleep(sleep_seconds)
                
                # Wait for exact time to avoid sending reports a few seconds early
                while datetime.now() < next_time:
                    await asyncio.sleep(0.1)  # Small delay to hit exact time
                
                # Additional delay to ensure data has been updated after stock refresh
                delay_seconds = self.settings.report_delay_after_stock_update
                logger.info(f"⏰ Waiting additional {delay_seconds} seconds for data to update after stock refresh...")
                await asyncio.sleep(delay_seconds)
                
                # Send full report if we're still running
                if self.is_running and not self._shutdown_event.is_set():
                    actual_time = datetime.now()
                    logger.info(f"Sending full report at {actual_time.strftime('%H:%M:%S')} ({delay_seconds}s after scheduled time)")
                    await self._send_full_update()
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                if self.is_running and not self._shutdown_event.is_set():
                    await asyncio.sleep(60)  # Wait longer on error
        
        logger.info("Scheduler loop ended")
    
    async def _process_shop_data(self, shop_data: ShopData) -> None:
        """Process new shop data and send updates."""
        from datetime import datetime
        
        data_time = shop_data.timestamp.strftime("%H:%M:%S")
        logger.debug(f"Processing shop data from {data_time} with {len(shop_data.items)} items")
        
        # Filter items according to our rules
        filtered_items = shop_data.get_filtered_items(self.item_filter)
        
        # Update current shop data
        self.current_shop_data = shop_data
        logger.debug(f"Updated current shop data timestamp to {data_time}")
        
        # Detect new items
        new_items = self._detect_new_items(filtered_items)
        
        if new_items:
            logger.info(f"Detected {len(new_items)} new items at {data_time}")
            # Send new items update immediately
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
        """Send full shop report to the full channel with fresh data."""
        try:
            # Log exact time when report creation starts
            report_start_time = datetime.now()
            logger.info(f"🕐 Starting full report creation at {report_start_time.strftime('%H:%M:%S.%f')[:-3]}")
            
            # Always fetch fresh data for full reports to avoid stale data
            logger.info("Fetching fresh shop data for full report")
            fresh_shop_data = await self.websocket_client.fetch_shop_data()
            
            if not fresh_shop_data:
                logger.warning("No fresh shop data available, using cached data")
                shop_data = self.current_shop_data
                if not shop_data:
                    logger.error("No shop data available for full update")
                    return
                data_time = shop_data.timestamp.strftime("%H:%M:%S")
                logger.info(f"Using cached shop data from {data_time}")
            else:
                shop_data = fresh_shop_data
                # Update current shop data with fresh data
                self.current_shop_data = fresh_shop_data
                data_time = shop_data.timestamp.strftime("%H:%M:%S")
                logger.info(f"Using fresh shop data from {data_time}")
            
            # Filter items for full report
            filtered_items = shop_data.get_filtered_items(self.item_filter)
            
            if not filtered_items:
                logger.info("No items to include in full update - sending empty report")
                # Send empty report instead of skipping
                message = self.message_formatter.format_full_report_message(
                    [],
                    shop_data.timestamp
                )
            else:
                # Format full report message with items
                message = self.message_formatter.format_full_report_message(
                    filtered_items,
                    shop_data.timestamp
                )
            
            # Send message to full channel
            send_time = datetime.now()
            logger.info(f"📤 Sending full report at {send_time.strftime('%H:%M:%S.%f')[:-3]} with data timestamp {data_time}")
            success = await self.telegram_bot.send_to_full_channel(message)
            
            if success:
                item_count = len(filtered_items) if filtered_items else 0
                complete_time = datetime.now()
                duration = (complete_time - report_start_time).total_seconds()
                logger.info(f"✅ Full report completed at {complete_time.strftime('%H:%M:%S.%f')[:-3]} ({duration:.2f}s) with {item_count} items")
            else:
                logger.error("❌ Failed to send full update")
            
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
            
            # Send message to full channel
            logger.info("Sending initial report")
            success = await self.telegram_bot.send_to_full_channel(message)
            
            if success:
                logger.info(f"Initial full report sent with {len(filtered_items)} items")
            else:
                logger.error("Failed to send initial full report")
                
        except Exception as e:
            logger.error(f"Failed to send initial full report: {e}")
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler():
            logger.info("🛑 Received shutdown signal, gracefully stopping...")
            self._shutdown_event.set()
            self.is_running = False
        
        # Handle SIGINT (Ctrl+C) and SIGTERM
        try:
            if hasattr(signal, 'SIGINT'):
                signal.signal(signal.SIGINT, lambda s, f: signal_handler())
            if hasattr(signal, 'SIGTERM'):
                signal.signal(signal.SIGTERM, lambda s, f: signal_handler())
        except Exception as e:
            logger.warning(f"Could not setup signal handlers: {e}")
