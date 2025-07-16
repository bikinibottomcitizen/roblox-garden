#!/usr/bin/env python3
"""
Запуск парсера Roblox Garden без Telegram интеграции.
Подходит для тестирования и отладки.
"""

import asyncio
import os
from datetime import datetime
from roblox_garden.config.settings import Settings
from roblox_garden.websocket.client import WebSocketClient
from roblox_garden.filters.item_filters import RobloxGardenFilter
from roblox_garden.utils.formatters import MessageFormatter


async def run_parser_demo():
    """Запуск парсера в демо режиме без Telegram."""
    print("🚀 Roblox Garden Parser - Демо режим")
    print("=" * 50)
    print("📌 Запуск без Telegram интеграции")
    print("📌 Мониторинг Divine+ предметов каждые 30 секунд")
    print("📌 Нажмите Ctrl+C для остановки")
    print("=" * 50)
    
    # Настройка mock окружения для демо
    os.environ.update({
        'TELEGRAM_BOT_TOKEN': 'demo_token',
        'TELEGRAM_FULL_CHANNEL_ID': '-1001234567890',
        'TELEGRAM_UPDATES_CHANNEL_ID': '-1001234567891',
        'LOG_LEVEL': 'INFO'
    })
    
    settings = Settings()
    client = WebSocketClient(settings)
    filter_instance = RobloxGardenFilter.create_combined_filter()
    formatter = MessageFormatter(settings)
    
    previous_items = set()
    iteration = 0
    
    try:
        await client.connect()
        
        while True:
            iteration += 1
            current_time = datetime.now().strftime("%H:%M:%S")
            
            print(f"\n🕐 Итерация {iteration} - {current_time}")
            print("-" * 40)
            
            # Получаем данные
            shop_data = await client.fetch_shop_data()
            
            if not shop_data:
                print("❌ Не удалось получить данные")
                await asyncio.sleep(30)
                continue
            
            # Фильтруем Divine+ предметы
            filtered_items = shop_data.get_filtered_items(filter_instance)
            current_items = set()
            
            print(f"📦 Всего предметов в магазине: {len(shop_data.items)}")
            print(f"✨ Divine+ предметов: {len(filtered_items)}")
            
            if filtered_items:
                print("\n🔍 Divine+ предметы в наличии:")
                for item in filtered_items:
                    item_key = f"{item.name}_{item.quantity}_{item.in_stock}"
                    current_items.add(item_key)
                    
                    status_icon = "✅" if item.in_stock else "❌"
                    print(f"  {status_icon} {item.name} [{item.rarity.value}] - {item.quantity} шт.")
                
                # Показываем форматированные сообщения
                new_items_msg = formatter.format_new_items_message(filtered_items[:3])  # Первые 3
                full_report_msg = formatter.format_full_report_message(filtered_items, shop_data.timestamp)
                
                print(f"\n📨 Сообщение для канала обновлений:")
                print("-" * 30)
                print(new_items_msg)
                
                print(f"\n📋 Полный отчет:")
                print("-" * 30)
                print(full_report_msg)
            else:
                print("  🔍 Нет Divine+ предметов в наличии")
            
            # Проверяем изменения
            if iteration > 1:
                if current_items != previous_items:
                    print("\n🚨 ОБНАРУЖЕНЫ ИЗМЕНЕНИЯ В СТОКЕ:")
                    added = current_items - previous_items
                    removed = previous_items - current_items
                    
                    if added:
                        print("  ➕ Новые предметы:", ", ".join([item.split("_")[0] for item in added]))
                    if removed:
                        print("  ➖ Убрано из стока:", ", ".join([item.split("_")[0] for item in removed]))
                        
                    # В реальном режиме здесь бы отправлялось уведомление в Telegram
                    print("  📱 (В боевом режиме было бы отправлено уведомление в Telegram)")
                else:
                    print("\n🔄 Сток не изменился")
            
            previous_items = current_items
            
            print(f"\n⏳ Ожидание следующего обновления (30 сек)...")
            await asyncio.sleep(30)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Остановка по запросу пользователя")
    
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()
        print("\n✅ Парсер остановлен")
        print("🔌 Соединение закрыто")
        print("Спасибо за использование Roblox Garden Parser! 🌱")


async def main():
    """Главная функция."""
    await run_parser_demo()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
