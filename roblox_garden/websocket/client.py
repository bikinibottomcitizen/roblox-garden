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
    
    class websockets:
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
    
    @classmethod
    def get_item_rarity(cls, name: str) -> Rarity:
        """Get item rarity from database."""
        return cls.ITEM_RARITIES.get(name, Rarity.UNKNOWN)


class WebSocketClient:
    """WebSocket client for Roblox Garden API."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = None
        self._last_shop_data = None
        
        # API endpoints
        self.base_url = settings.roblox_api_base_url
        self.http_url = f"{self.base_url}/alldata"
    
    async def connect(self) -> None:
        """Connect to the API."""
        try:
            logger.info(f"🔍 Подключение к Roblox Garden API...")
            
            # Инициализация HTTP сессии
            if aiohttp is None:
                raise ImportError("aiohttp is required for API connection")
                
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            logger.info("✅ API клиент инициализирован")
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к API: {e}")
            raise
    
    async def close(self) -> None:
        """Close the connection."""
        if self.session:
            await self.session.close()
        logger.info("🔌 Соединение закрыто")
    
    async def listen(self) -> AsyncGenerator[ShopData, None]:
        """Listen for shop data updates."""
        logger.info("🎯 Начинаем мониторинг обновлений магазина...")
        
        iteration = 0
        while True:  # Infinite loop with proper error handling
            try:
                iteration += 1
                # Fetch shop data from HTTP API
                shop_data = await self._fetch_shop_data()
                
                if shop_data:
                    logger.debug(f"📊 Получены данные: {len(shop_data.items)} предметов")
                    yield shop_data
                
                # Wait before next poll
                poll_interval = getattr(self.settings, 'API_POLL_INTERVAL', 30)
                await asyncio.sleep(poll_interval)
                
            except asyncio.CancelledError:
                logger.info("🛑 Мониторинг остановлен")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле мониторинга: {e}")
                await asyncio.sleep(10)  # Wait before retry
    
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
        
        # Parse different item categories based on real API structure
        if 'seeds' in data and isinstance(data['seeds'], list):
            items.extend(self._parse_items(data['seeds'], ItemType.SEED))
        
        if 'gear' in data and isinstance(data['gear'], list):
            items.extend(self._parse_items(data['gear'], ItemType.GEAR))
        
        if 'eggs' in data and isinstance(data['eggs'], list):
            items.extend(self._parse_items(data['eggs'], ItemType.EGG))
            
        if 'honey' in data and isinstance(data['honey'], list):
            items.extend(self._parse_items(data['honey'], ItemType.HONEY))
            
        if 'cosmetics' in data and isinstance(data['cosmetics'], list):
            items.extend(self._parse_items(data['cosmetics'], ItemType.COSMETIC))
        
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
            
            rarity = StaticRarityDatabase.get_item_rarity(name, item_type)
            
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
