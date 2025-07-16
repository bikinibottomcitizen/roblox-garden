#!/usr/bin/env python3
"""
Демонстрационный скрипт для тестирования Roblox Garden Parser
без реальной отправки в Telegram.
"""

import asyncio
import os
from datetime import datetime

from roblox_garden.config.settings import Settings
from roblox_garden.websocket.client import WebSocketClient
from roblox_garden.filters.item_filters import RobloxGardenFilter
from roblox_garden.utils.formatters import MessageFormatter


async def demo_parser():
    """Демонстрация работы парсера."""
    
    # Настройка mock окружения
    os.environ.update({
        'TELEGRAM_BOT_TOKEN': 'demo_token',
        'TELEGRAM_FULL_CHANNEL_ID': '-1001234567890',
        'TELEGRAM_UPDATES_CHANNEL_ID': '-1001234567891',
        'LOG_LEVEL': 'INFO'
    })
    
    print("🚀 Запуск демонстрации Roblox Garden Parser")
    print("=" * 50)
    
    # Инициализация компонентов
    settings = Settings()
    client = WebSocketClient(settings)
    formatter = MessageFormatter(settings)
    item_filter = RobloxGardenFilter.create_combined_filter()
    
    try:
        # Подключение к API
        print("📡 Подключение к Roblox Garden API...")
        await client.connect()
        
        iteration = 0
        
        # Мониторинг обновлений
        async for shop_data in client.listen():
            iteration += 1
            print(f"\n📊 Итерация {iteration} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Статистика по всем предметам
            all_items = shop_data.items
            print(f"Всего предметов в магазине: {len(all_items)}")
            
            # Группировка по типам
            seeds = [item for item in all_items if item.type.value == 'seed']
            gears = [item for item in all_items if item.type.value == 'gear']  
            eggs = [item for item in all_items if item.type.value == 'egg']
            
            print(f"├─ 🌱 Семена: {len(seeds)}")
            print(f"├─ ⚙️ Гиры: {len(gears)}")
            print(f"└─ 🥚 Яйца: {len(eggs)}")
            
            # Применение фильтров
            filtered_items = [item for item in all_items if item_filter.should_include(item)]
            
            if filtered_items:
                print(f"\n✨ Найдено {len(filtered_items)} подходящих предметов:")
                
                for item in filtered_items:
                    status = "✅ В наличии" if item.in_stock else "❌ Отсутствует"
                    print(f"  {item.get_emoji()} [{item.rarity.value}] {item.name} ({item.quantity}шт) - {status}")
                
                # Демонстрация форматирования сообщений
                print(f"\n📱 Сообщение для канала обновлений:")
                print("-" * 30)
                update_message = formatter.format_new_items_message(filtered_items)
                print(update_message)
                
                print(f"\n📋 Полный отчет:")
                print("-" * 30)
                full_report = formatter.format_full_report_message(filtered_items, shop_data.timestamp)
                print(full_report)
                
            else:
                print("\n❌ Нет предметов, соответствующих фильтрам")
                print("   (Ищем семена/гиры Divine+ и разрешенные яйца)")
            
            # Остановимся после 3 итераций для демонстрации
            if iteration >= 3:
                print(f"\n✅ Демонстрация завершена после {iteration} итераций")
                break
            
            print(f"\n⏳ Ожидание следующего обновления (30 сек)...")
            
    except KeyboardInterrupt:
        print("\n🛑 Остановлено пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()
        print("\n🔌 Соединение закрыто")


if __name__ == "__main__":
    print("Roblox Garden Parser Demo")
    print("Нажмите Ctrl+C для остановки")
    print()
    
    try:
        asyncio.run(demo_parser())
    except KeyboardInterrupt:
        print("\nДемонстрация прервана")
    
    print("Спасибо за использование Roblox Garden Parser! 🌱")
