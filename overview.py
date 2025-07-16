#!/usr/bin/env python3

"""
Демонстрация всех доступных скриптов и возможностей Roblox Garden Bot.
"""

import os
import sys

def print_header(title):
    """Красивый заголовок."""
    print(f"\n{'=' * 60}")
    print(f"🎯 {title}")
    print(f"{'=' * 60}")

def print_script_info(script, description, emoji="📄"):
    """Информация о скрипте."""
    exists = "✅" if os.path.exists(script) else "❌"
    print(f"{exists} {emoji} {script:<25} - {description}")

def main():
    """Главная функция демонстрации."""
    print("🤖 ROBLOX GARDEN BOT - ПОЛНЫЙ ОБЗОР ВОЗМОЖНОСТЕЙ")
    print("=" * 60)
    print("Добро пожаловать в систему мониторинга Roblox Garden!")
    
    print_header("ОСНОВНЫЕ СКРИПТЫ")
    print_script_info("get_channel_ids.py", "Настройка ID каналов Telegram", "🔍")
    print_script_info("demo_channel_ids.py", "Демо настройки каналов", "🎯")
    print_script_info("python -m roblox_garden", "Запуск основного приложения", "🚀")
    print_script_info("demo.py", "Демонстрация парсера без Telegram", "📊")
    
    print_header("ТЕСТИРОВАНИЕ И ОТЛАДКА")
    print_script_info("test_telegram.py", "Тестирование Telegram бота", "🔧")
    print_script_info("debug_api.py", "Отладка API данных", "🐛")
    print_script_info("monitor_api.py", "Мониторинг изменений API", "📈")
    print_script_info("test_channel_ids.py", "Тесты настройки каналов", "🧪")
    
    print_header("DOCKER РАЗВЕРТЫВАНИЕ")
    print_script_info("deploy.sh", "Развертывание в Docker (dev)", "🐳")
    print_script_info("deploy-prod.sh", "Продакшн развертывание", "🏭")
    print_script_info("health_check.sh", "Проверка состояния системы", "❤️")
    
    print_header("СПЕЦИАЛЬНЫЕ ТЕСТЫ")
    print_script_info("test_formatting.py", "Тестирование форматирования", "✨")
    print_script_info("test_intervals.py", "Тестирование интервалов", "⏰")
    print_script_info("test_docker_deployment.py", "Валидация Docker инфраструктуры", "🐳")
    
    print_header("БЫСТРЫЙ СТАРТ")
    print("1️⃣  Настройка каналов:")
    print("    python get_channel_ids.py")
    print("")
    print("2️⃣  Локальный запуск:")
    print("    python -m roblox_garden")
    print("")
    print("3️⃣  Docker развертывание:")
    print("    ./deploy.sh")
    print("")
    print("4️⃣  Демонстрация без настройки:")
    print("    python demo.py")
    
    print_header("АРХИТЕКТУРА СИСТЕМЫ")
    print("📦 roblox_garden/")
    print("├── core/           🧠 Основная логика приложения")
    print("├── models/         📋 Модели данных (Pydantic)")
    print("├── filters/        🔍 Фильтры предметов по редкости")
    print("├── telegram/       📱 Telegram бот интеграция")
    print("├── websocket/      🌐 WebSocket клиент")
    print("├── utils/          🛠️ Утилиты и форматирование")
    print("└── config/         ⚙️ Конфигурация и настройки")
    
    print_header("МОНИТОРИРУЕМЫЕ ПРЕДМЕТЫ")
    print("🌱 Семена:")
    print("   • Giant Pinecone (Divine)")
    print("   • Beanstalk (Divine)")
    print("   • Tree Branch (Divine)")
    print("   • Magic Beans (Legendary)")
    print("   • Lucky Clover (Mythical)")
    print("   • Magical Seed (Transcendent)")
    print("   • Rainbow Flower (Prismatic)")
    print("")
    print("⚙️ Гиры:")
    print("   • Watering Can (Divine)")
    print("   • Magic Shears (Legendary)")
    print("   • Upgrade Juice (Mythical)")
    print("   • Sprinkler (Transcendent)")
    print("   • Fertilizer (Prismatic)")
    print("")
    print("🥚 Яйца:")
    print("   • Bee Egg (Mythical)")
    print("   • Paradise Egg (Transcendent)")
    print("   • Bug Egg (Prismatic)")
    
    print_header("КАНАЛЫ TELEGRAM")
    print("📱 Канал обновлений:")
    print("   • Краткие уведомления о новых товарах")
    print("   • Только Divine+ редкость")
    print("   • Мгновенные push-уведомления")
    print("")
    print("📊 Канал полного отчета:")
    print("   • Детальная информация о всех товарах")
    print("   • Цены и количество")
    print("   • Регулярные обновления каждые 5 минут")
    
    print_header("ТЕХНИЧЕСКИЕ ОСОБЕННОСТИ")
    print("🔄 WebSocket подключение к API Roblox Garden")
    print("📊 Статическая база данных редкостей (19 предметов)")
    print("💰 Интеграция цен из базы данных")
    print("🎯 Умная фильтрация по типу и редкости")
    print("🔧 Graceful reconnection при потере соединения")
    print("📝 Подробное логирование всех операций")
    print("🐳 Полная контейнеризация с Docker")
    print("🔒 Поддержка Docker Secrets для продакшна")
    
    print_header("ДОКУМЕНТАЦИЯ")
    print("📖 README.md           - Основная документация")
    print("📚 CHANNEL_SETUP.md    - Настройка каналов")
    print("🐳 DOCKER.md           - Docker развертывание")
    print("📋 SETUP.md            - Установка и настройка")
    
    print_header("ПОДДЕРЖКА")
    print("🐛 Issues: https://github.com/bikinibottomcitizen/roblox-garden/issues")
    print("💬 Discussions: https://github.com/bikinibottomcitizen/roblox-garden/discussions")
    print("📧 Email: support@example.com")
    
    print(f"\n🎉 ГОТОВО К ИСПОЛЬЗОВАНИЮ!")
    print("Выберите нужный скрипт и следуйте инструкциям.")
    print("Для быстрого старта используйте: python get_channel_ids.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Обзор прерван пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка в обзоре: {e}")
        sys.exit(1)
