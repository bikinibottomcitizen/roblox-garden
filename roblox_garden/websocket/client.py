"""
WebSocket client for connecting to Roblox Garden API.
"""

import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator, Optional, Dict, Any

try:
    import websockets
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    
    # Mock websockets for development
    class MockWebSocket:
        async def __aiter__(self):
            return self
        
        async def __anext__(self):
            await asyncio.sleep(1)
            raise StopAsyncIteration
    
    class MockWebsockets:
        @staticmethod
        async def connect(uri):
            return MockWebSocket()

try:
    import aiohttp
except ImportError:
    aiohttp = None

from roblox_garden.config.settings import Settings
from roblox_garden.models.shop import ShopData, ShopItem, ItemType, Rarity
from roblox_garden.utils.static_rarity_db import StaticRarityDatabase


class ItemDatabase:
    """Static database of known items and their properties."""
    
    # Known rarities for items (пополняется по мере изучения игры)
    ITEM_RARITIES = {
        # === SEEDS ===
        # Divine and higher seeds
        "Giant Pinecone": Rarity.DIVINE,
        "Burning Bud": Rarity.DIVINE,
        "Cacao": Rarity.DIVINE,
        "Dragon Fruit": Rarity.DIVINE,
        "Ember Lily": Rarity.DIVINE,
        "Grape": Rarity.DIVINE,
        "Mango": Rarity.DIVINE,
        "Mushroom": Rarity.DIVINE,
        "Pepper": Rarity.DIVINE,
        "Sugar Apple": Rarity.DIVINE,
        "Beanstalk": Rarity.DIVINE,
        
        # Common seeds (низкая редкость - будут отфильтрованы)
        "Carrot": Rarity.COMMON,
        "Strawberry": Rarity.COMMON,
        "Watermelon": Rarity.COMMON,
        "Tomato": Rarity.COMMON,
        "Blueberry": Rarity.COMMON,
        "Corn": Rarity.COMMON,
        "Potato": Rarity.COMMON,
        "Onion": Rarity.COMMON,
        "Pumpkin": Rarity.RARE,
        "Sunflower": Rarity.UNCOMMON,
        
        # === GEARS ===
        # Divine and higher gears
        "Master Sprinkler": Rarity.DIVINE,
        "Godly Sprinkler": Rarity.DIVINE,
        "Levelup Lollipop": Rarity.DIVINE,
        "Tanning Mirror": Rarity.DIVINE,
        "Friendship Pot": Rarity.DIVINE,
        
        # Excluded gears (исключаем по требованию)
        "Harvest Tool": Rarity.DIVINE,
        "Favorite Tool": Rarity.DIVINE,
        "Cleaning Spray": Rarity.DIVINE,
        
        # Common gears (низкая редкость)
        "Recall Wrench": Rarity.COMMON,
        "Basic Sprinkler": Rarity.COMMON,
        "Trowel": Rarity.COMMON,
        "Watering Can": Rarity.COMMON,
        
        # === EGGS ===
        # Allowed eggs only
        "Paradise Egg": Rarity.MYTHICAL,
        "Bug Egg": Rarity.DIVINE,
        "Mythical Egg": Rarity.MYTHIC,
        "Bee Egg": Rarity.DIVINE,
        
        # Other eggs (будут отфильтрованы)
        "Common Egg": Rarity.COMMON,
        "Dragon Egg": Rarity.LEGENDARY,  # Не в списке разрешенных
        "Fire Egg": Rarity.RARE,
        "Water Egg": Rarity.RARE,
        "Earth Egg": Rarity.RARE,
    }
    
    @classmethod
    def get_item_type(cls, name: str) -> ItemType:
        """Determine item type by name patterns."""
        name_lower = name.lower()
        
        if "egg" in name_lower:
            return ItemType.EGG
        elif any(gear_word in name_lower for gear_word in [
            "tool", "sprinkler", "wrench", "lollipop", "mirror", "pot", 
            "trowel", "can", "spray", "fertilizer"
        ]):
            return ItemType.GEAR
        else:
            return ItemType.SEED  # Default to seed


class WebSocketClient:
    """WebSocket client for Roblox Garden API."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = None
        self._last_shop_data = None
        self._is_connected = False
        
        # API endpoints
        self.base_url = settings.roblox_api_base_url
        self.http_url = f"{self.base_url}/alldata"
    
    async def connect(self) -> None:
        """Connect to the API."""
        try:
            logger.info(f"🔍 Подключение к Roblox Garden API...")
            
            # Close existing session if any
            if self.session and not self.session.closed:
                await self.session.close()
            
            # Инициализация HTTP сессии
            if aiohttp is None:
                raise ImportError("aiohttp is required for API connection")
                
            # Create session with SSL verification disabled for problematic endpoints
            connector = aiohttp.TCPConnector(
                ssl=False,  # Disable SSL verification if needed
                limit=10,
                limit_per_host=5,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=30, connect=10),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
            )
            
            self._is_connected = True
            logger.info("✅ API клиент инициализирован")
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к API: {e}")
            self._is_connected = False
            raise
    
    async def close(self) -> None:
        """Close the connection gracefully."""
        try:
            self._is_connected = False
            if self.session and not self.session.closed:
                # Close all pending connections gracefully
                await self.session.close()
                # Wait a bit for cleanup
                await asyncio.sleep(0.1)
            logger.info("🔌 Соединение закрыто")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при закрытии соединения: {e}")
    
    async def listen(self) -> AsyncGenerator[ShopData, None]:
        """Listen for shop data updates with robust error handling."""
        logger.info("🎯 Начинаем мониторинг обновлений магазина...")
        
        iteration = 0
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self._is_connected:
            try:
                iteration += 1
                consecutive_errors = 0  # Reset error counter on successful iteration
                
                # Ensure we have a valid session
                if not self.session or self.session.closed:
                    logger.info("🔄 Переподключение к API...")
                    await self.connect()
                
                # Fetch shop data from HTTP API
                shop_data = await self._fetch_shop_data()
                
                if shop_data:
                    logger.debug(f"📊 Получены данные: {len(shop_data.items)} предметов")
                    yield shop_data
                else:
                    logger.warning("⚠️ Получены пустые данные от API")
                
                # Wait before next poll
                poll_interval = getattr(self.settings, 'shop_check_interval', 30)
                await asyncio.sleep(poll_interval)
                
            except asyncio.CancelledError:
                logger.info("🛑 Мониторинг остановлен")
                break
                
            except Exception as e:
                # Handle aiohttp specific exceptions if available
                if aiohttp and (isinstance(e, aiohttp.ClientConnectionError) or isinstance(e, aiohttp.ClientError)):
                    consecutive_errors += 1
                    logger.error(f"❌ Ошибка соединения (попытка {consecutive_errors}): {e}")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error(f"💥 Превышено максимальное количество ошибок ({max_consecutive_errors})")
                        break
                    
                    # Reconnect on connection errors
                    await self._handle_connection_error()
                    continue
                    
                # Handle other exceptions
                consecutive_errors += 1
                logger.error(f"❌ Неожиданная ошибка в цикле мониторинга: {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.error(f"💥 Превышено максимальное количество ошибок ({max_consecutive_errors})")
                    break
                    
                await asyncio.sleep(min(10 * consecutive_errors, 60))  # Exponential backoff
    
    async def _handle_connection_error(self) -> None:
        """Handle connection errors with proper cleanup and reconnection."""
        try:
            # Close current session
            if self.session and not self.session.closed:
                await self.session.close()
                await asyncio.sleep(0.5)  # Wait for cleanup
            
            # Wait before reconnecting
            await asyncio.sleep(5)
            
            # Reconnect
            await self.connect()
            
        except Exception as e:
            logger.error(f"❌ Ошибка при переподключении: {e}")
            await asyncio.sleep(10)
    
    async def fetch_shop_data(self) -> Optional[ShopData]:
        """Public method to fetch shop data once."""
        if not self.session:
            # Initialize session if not already done
            await self.connect()
        
        return await self._fetch_shop_data()
    
    async def _fetch_shop_data(self) -> Optional[ShopData]:
        """Fetch shop data from HTTP API."""
        if not self.session:
            logger.warning("⚠️ Сессия не инициализирована")
            return None
        
        try:
            async with self.session.get(self.http_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_shop_data(data)
                else:
                    logger.error(f"❌ HTTP {response.status} при запросе к {self.http_url}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Ошибка при получении данных: {e}")
            return None
    
    def _parse_shop_data(self, data: Dict[str, Any]) -> ShopData:
        """Parse shop data from API response using rarity parser."""
        items = []
        
        # Parse only relevant item categories (seeds, gear, eggs)
        if 'seeds' in data and isinstance(data['seeds'], list):
            items.extend(self._parse_items(data['seeds'], ItemType.SEED))
        
        if 'gear' in data and isinstance(data['gear'], list):
            items.extend(self._parse_items(data['gear'], ItemType.GEAR))
        
        if 'eggs' in data and isinstance(data['eggs'], list):
            items.extend(self._parse_items(data['eggs'], ItemType.EGG))
            
        # Игнорируем honey и cosmetics - они не нужны для фильтрации
        
        # Create shop data
        shop_data = ShopData(
            timestamp=datetime.now(),
            items=items
        )
        shop_data.calculate_stats()
        
        logger.debug(f"📦 Обработано {len(items)} предметов из API")
        return shop_data
    
    def _parse_items(self, items_data: list, default_type: ItemType) -> list[ShopItem]:
        """Parse items of a specific type using rarity parser."""
        items = []
        
        for item_data in items_data:
            if not isinstance(item_data, dict) or 'name' not in item_data:
                continue
                
            name = item_data['name']
            quantity = item_data.get('quantity', 0)
            
            # Get rarity from static database
            # Сначала определяем правильный тип предмета
            item_type = StaticRarityDatabase.get_item_type(name)
            if item_type == ItemType.UNKNOWN:
                item_type = default_type
            
            rarity = StaticRarityDatabase.get_rarity(name, item_type)
            
            # Create shop item
            item = ShopItem(
                id=f"{item_type.value}_{name.replace(' ', '_').lower()}",
                name=name,
                type=item_type,
                rarity=rarity,
                quantity=quantity,
                in_stock=quantity > 0
            )
            
            items.append(item)
        
        return items
    
    def _create_mock_data(self) -> ShopData:
        """Create mock shop data for testing."""
        mock_items = [
            ShopItem(
                id="Giant Pinecone",
                name="Giant Pinecone",
                type=ItemType.SEED,
                rarity=Rarity.DIVINE,
                quantity=1,
                in_stock=True
            ),
            ShopItem(
                id="Master Sprinkler",
                name="Master Sprinkler",
                type=ItemType.GEAR,
                rarity=Rarity.DIVINE,
                quantity=1,
                in_stock=True
            ),
            ShopItem(
                id="Paradise Egg",
                name="Paradise Egg",
                type=ItemType.EGG,
                rarity=Rarity.MYTHICAL,
                quantity=1,
                in_stock=True
            ),
            ShopItem(
                id="Harvest Tool",
                name="Harvest Tool",
                type=ItemType.GEAR,
                rarity=Rarity.DIVINE,
                quantity=1,
                in_stock=True
            ),
            ShopItem(
                id="Carrot",
                name="Carrot",
                type=ItemType.SEED,
                rarity=Rarity.COMMON,
                quantity=13,
                in_stock=True
            ),
        ]
        
        shop_data = ShopData(
            timestamp=datetime.now(),
            items=mock_items
        )
        shop_data.calculate_stats()
        
        return shop_data
