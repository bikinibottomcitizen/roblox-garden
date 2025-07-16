#!/usr/bin/env python3
"""
Проверка конкретного предмета Advanced Sprinkler.
"""

import asyncio
from roblox_garden.config.settings import Settings
from roblox_garden.websocket.client import WebSocketClient
from roblox_garden.filters.item_filters import RobloxGardenFilter
from roblox_garden.utils.static_rarity_db import StaticRarityDatabase
from roblox_garden.models.shop import ItemType

async def check_advanced_sprinkler():
    """Проверка Advanced Sprinkler."""
    print("🔍 Проверка Advanced Sprinkler")
    print("=" * 40)
    
    settings = Settings()
    client = WebSocketClient(settings)
    
    try:
        # Получаем данные
        shop_data = await client.fetch_shop_data()
        
        if not shop_data:
            print("❌ Не удалось получить данные")
            return
        
        # Ищем Advanced Sprinkler
        advanced_sprinkler = None
        for item in shop_data.items:
            if item.name == "Advanced Sprinkler":
                advanced_sprinkler = item
                break
        
        if advanced_sprinkler:
            print(f"✅ Найден: {advanced_sprinkler.name}")
            print(f"   Тип: {advanced_sprinkler.type.value}")
            print(f"   Редкость: {advanced_sprinkler.rarity.value}")
            print(f"   Количество: {advanced_sprinkler.quantity}")
            print(f"   В наличии: {'✅' if advanced_sprinkler.in_stock else '❌'}")
            
            # Проверяем что в статической базе
            static_rarity = StaticRarityDatabase.get_item_rarity("Advanced Sprinkler", ItemType.GEAR)
            print(f"   Редкость в базе: {static_rarity.value}")
            
            # Проверяем фильтры
            filter_instance = RobloxGardenFilter.create_combined_filter()
            passes_filter = filter_instance.should_include(advanced_sprinkler)
            print(f"   Проходит фильтр Divine+: {'✅' if passes_filter else '❌'}")
            
            # Объясняем почему
            if not passes_filter:
                print(f"   ❌ НЕ проходит, так как {advanced_sprinkler.rarity.value} < Divine")
                print(f"   📝 Нужна редкость Divine или выше для фильтрации")
            
        else:
            print("❌ Advanced Sprinkler не найден в данных")
            print("\n📋 Доступные gear предметы:")
            for item in shop_data.items:
                if item.type.value == "gear":
                    print(f"  • {item.name} [{item.rarity.value}]")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(check_advanced_sprinkler())
