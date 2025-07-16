#!/usr/bin/env python3
"""
Тест для проверки различий в данных между запросами
и проверки логики фильтрации в реальном времени.
"""

import asyncio
import json
from datetime import datetime
from roblox_garden.config.settings import Settings
from roblox_garden.websocket.client import WebSocketClient
from roblox_garden.filters.item_filters import RobloxGardenFilter

async def monitor_api_changes():
    """Мониторинг изменений в API в реальном времени."""
    print("📊 Мониторинг изменений API в реальном времени")
    print("=" * 60)
    
    settings = Settings()
    client = WebSocketClient(settings)
    filter_instance = RobloxGardenFilter.create_combined_filter()
    
    previous_divine_items = set()
    iteration = 0
    
    try:
        await client.connect()
        
        while iteration < 5:  # 5 итераций для проверки
            iteration += 1
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"\n🕐 Итерация {iteration} - {current_time}")
            print("-" * 40)
            
            # Получаем свежие данные
            shop_data = await client.fetch_shop_data()
            
            if not shop_data:
                print("❌ Не удалось получить данные")
                continue
            
            # Фильтруем Divine+ предметы
            filtered_items = shop_data.get_filtered_items(filter_instance)
            current_divine_items = set()
            
            print(f"📦 Всего предметов: {len(shop_data.items)}")
            print(f"✨ Divine+ предметов: {len(filtered_items)}")
            
            if filtered_items:
                print("\n🔍 Divine+ предметы:")
                for item in filtered_items:
                    item_key = f"{item.name}_{item.quantity}_{item.in_stock}"
                    current_divine_items.add(item_key)
                    
                    status_icon = "✅" if item.in_stock else "❌"
                    print(f"  {status_icon} {item.name} [{item.rarity.value}] - {item.quantity} шт.")
            else:
                print("  Нет Divine+ предметов")
            
            # Проверяем изменения
            if iteration > 1:
                if current_divine_items != previous_divine_items:
                    print("\n🚨 ОБНАРУЖЕНЫ ИЗМЕНЕНИЯ:")
                    added = current_divine_items - previous_divine_items
                    removed = previous_divine_items - current_divine_items
                    
                    if added:
                        print("  ➕ Добавлено:", added)
                    if removed:
                        print("  ➖ Удалено:", removed)
                else:
                    print("\n🔄 Изменений нет")
            
            previous_divine_items = current_divine_items
            
            # Проверим также предметы с quantity = 0
            zero_quantity_items = [item for item in shop_data.items if item.quantity == 0]
            if zero_quantity_items:
                print(f"\n⚠️  Предметы с quantity=0: {len(zero_quantity_items)}")
                for item in zero_quantity_items[:5]:  # Показываем первые 5
                    print(f"    {item.name} - {item.quantity} шт.")
            
            if iteration < 5:
                print("\n⏳ Ожидание 10 секунд...")
                await asyncio.sleep(10)
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(monitor_api_changes())
