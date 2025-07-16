"""
Парсер данных о редкости предметов с сайта growagardenpro.com
"""

import asyncio
import re
from typing import Dict, Optional, Set
from dataclasses import dataclass

try:
    import aiohttp
    from bs4 import BeautifulSoup
    from loguru import logger
except ImportError:
    import logging
    aiohttp = None
    BeautifulSoup = None
    logger = logging.getLogger(__name__)

from roblox_garden.models.shop import Rarity, ItemType


@dataclass
class CropInfo:
    """Информация о культуре с сайта."""
    name: str
    rarity: Rarity
    item_type: ItemType
    base_value: int
    available: bool = True


class RarityParser:
    """Парсер данных о редкости с growagardenpro.com"""
    
    BASE_URL = "https://growagardenpro.com"
    ENDPOINTS = {
        "crops": "/crops/",
        "gear": "/gear/", 
        "eggs": "/eggs/",
        "cosmetics": "/cosmetics/"
    }
    
    # Маппинг строк редкости в enum
    RARITY_MAPPING = {
        "Common": Rarity.COMMON,
        "Uncommon": Rarity.UNCOMMON, 
        "Rare": Rarity.RARE,
        "Legendary": Rarity.LEGENDARY,
        "Mythical": Rarity.MYTHICAL,
        "Divine": Rarity.DIVINE,
        "Prismatic": Rarity.PRISMATIC,
        "Unknown": Rarity.COMMON  # Fallback для неизвестных
    }
    
    # Маппинг категорий в типы предметов
    TYPE_MAPPING = {
        "crops": ItemType.SEED,
        "gear": ItemType.GEAR,
        "eggs": ItemType.EGG,
        "cosmetics": ItemType.COSMETIC
    }
    
    def __init__(self):
        self.session = None
        self._cached_data: Dict[str, CropInfo] = {}
        self._last_update = None
        self.cache_ttl = 3600  # 1 час
    
    async def __aenter__(self):
        """Async context manager entry."""
        if aiohttp is None:
            raise ImportError("aiohttp is required for RarityParser")
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Roblox Garden Parser)'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def fetch_all_rarities(self) -> Dict[str, CropInfo]:
        """Получить данные о редкости всех предметов."""
        if not self._should_refresh_cache():
            return self._cached_data
            
        logger.info("🔄 Обновление данных о редкости с growagardenpro.com...")
        
        all_items = {}
        
        for category, endpoint in self.ENDPOINTS.items():
            try:
                items = await self._fetch_category_data(category, endpoint)
                all_items.update(items)
                logger.info(f"✅ Загружено {len(items)} предметов из категории {category}")
                
                # Небольшая задержка между запросами
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ Ошибка при загрузке {category}: {e}")
                continue
        
        self._cached_data = all_items
        self._last_update = asyncio.get_event_loop().time()
        
        logger.info(f"🎯 Всего загружено {len(all_items)} предметов с данными о редкости")
        return all_items
    
    async def _fetch_category_data(self, category: str, endpoint: str) -> Dict[str, CropInfo]:
        """Получить данные для конкретной категории."""
        if not self.session:
            raise RuntimeError("Session not initialized")
            
        url = f"{self.BASE_URL}{endpoint}"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status} for {url}")
            
            html = await response.text()
            
        return self._parse_category_html(html, category)
    
    def _parse_category_html(self, html: str, category: str) -> Dict[str, CropInfo]:
        """Парсинг HTML страницы категории."""
        if BeautifulSoup is None:
            return self._parse_with_regex(html, category)
        
        return self._parse_with_bs4(html, category)
    
    def _parse_with_regex(self, html: str, category: str) -> Dict[str, CropInfo]:
        """Парсинг с помощью регулярных выражений (fallback)."""
        items = {}
        item_type = self.TYPE_MAPPING.get(category, ItemType.SEED)
        
        # Паттерн для поиска предметов: [Rarity] [Type] Name Name ...
        pattern = r'\[(\w+)\]\s*(?:\w+\s+)?([^[]+?)(?:Base Value:|Seed Price:|Available:)'
        
        matches = re.findall(pattern, html, re.IGNORECASE)
        
        for rarity_str, name_part in matches:
            # Очистка имени предмета
            name = re.sub(r'\s+', ' ', name_part).strip()
            name = re.sub(r'(Multi|Limited|Single)\s*', '', name).strip()
            
            if not name or len(name) < 2:
                continue
                
            rarity = self.RARITY_MAPPING.get(rarity_str, Rarity.COMMON)
            
            # Извлечение base value
            value_match = re.search(rf'{re.escape(name)}.*?Base Value:\s*Sheckle\s*([\d,]+)', html)
            base_value = 0
            if value_match:
                base_value = int(value_match.group(1).replace(',', ''))
            
            items[name] = CropInfo(
                name=name,
                rarity=rarity,
                item_type=item_type,
                base_value=base_value,
                available=True
            )
        
        return items
    
    def _parse_with_bs4(self, html: str, category: str) -> Dict[str, CropInfo]:
        """Парсинг с помощью BeautifulSoup."""
        # Пока используем regex fallback, так как структура сайта сложная
        return self._parse_with_regex(html, category)
    
    def _should_refresh_cache(self) -> bool:
        """Проверить, нужно ли обновить кеш."""
        if not self._cached_data or self._last_update is None:
            return True
            
        current_time = asyncio.get_event_loop().time()
        return (current_time - self._last_update) > self.cache_ttl
    
    def get_item_rarity(self, item_name: str) -> Optional[Rarity]:
        """Получить редкость предмета по имени."""
        crop_info = self._cached_data.get(item_name)
        return crop_info.rarity if crop_info else None
    
    def get_item_info(self, item_name: str) -> Optional[CropInfo]:
        """Получить полную информацию о предмете."""
        return self._cached_data.get(item_name)
    
    async def get_divine_plus_items(self) -> Set[str]:
        """Получить список предметов Divine редкости и выше."""
        await self.fetch_all_rarities()
        
        divine_plus = {Rarity.DIVINE, Rarity.PRISMATIC}
        
        return {
            name for name, info in self._cached_data.items()
            if info.rarity in divine_plus
        }


# Глобальный экземпляр парсера для использования в приложении
_global_parser: Optional[RarityParser] = None


async def get_rarity_parser() -> RarityParser:
    """Получить глобальный экземпляр парсера."""
    global _global_parser
    
    if _global_parser is None:
        _global_parser = RarityParser()
        async with _global_parser:
            await _global_parser.fetch_all_rarities()
    
    return _global_parser


async def get_item_rarity(item_name: str) -> Optional[Rarity]:
    """Быстрый способ получить редкость предмета."""
    parser = await get_rarity_parser()
    return parser.get_item_rarity(item_name)


# Для тестирования
if __name__ == "__main__":
    async def test_parser():
        """Тестирование парсера."""
        async with RarityParser() as parser:
            items = await parser.fetch_all_rarities()
            
            print(f"Загружено {len(items)} предметов")
            
            # Показать примеры Divine+ предметов
            divine_items = await parser.get_divine_plus_items()
            print(f"\nDivine+ предметы ({len(divine_items)}):")
            for item in sorted(list(divine_items))[:10]:
                info = parser.get_item_info(item)
                if info:
                    print(f"  {info.rarity.value}: {item}")
    
    asyncio.run(test_parser())
