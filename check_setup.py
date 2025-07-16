#!/usr/bin/env python3

"""
Быстрая проверка настроек и готовности системы Roblox Garden Bot.
"""

import os
import sys
from pathlib import Path

def check_file(filepath, description, required=True):
    """Проверить существование файла."""
    exists = os.path.exists(filepath)
    status = "✅" if exists else ("❌" if required else "⚠️")
    print(f"{status} {description}: {filepath}")
    return exists

def check_env_var(var_name, description, required=True):
    """Проверить переменную окружения."""
    value = os.getenv(var_name)
    has_value = value is not None and value.strip() != ""
    status = "✅" if has_value else ("❌" if required else "⚠️")
    display_value = "***" if has_value and "TOKEN" in var_name else (value or "не задана")
    print(f"{status} {description}: {display_value}")
    return has_value

def parse_env_file():
    """Парсинг .env файла."""
    env_vars = {}
    if os.path.exists('.env'):
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            print(f"⚠️ Ошибка чтения .env файла: {e}")
    return env_vars

def main():
    """Основная функция проверки."""
    print("🔍 ПРОВЕРКА ГОТОВНОСТИ ROBLOX GARDEN BOT")
    print("=" * 50)
    
    all_ok = True
    
    # Проверка основных файлов
    print("\n📁 ОСНОВНЫЕ ФАЙЛЫ:")
    files_to_check = [
        ("roblox_garden/__main__.py", "Главный модуль", True),
        ("roblox_garden/config/settings.py", "Настройки", True),
        ("roblox_garden/telegram/bot.py", "Telegram бот", True),
        ("requirements.txt", "Зависимости", True),
        (".env", "Переменные окружения", False),
        ("Dockerfile", "Docker образ", False),
        ("docker-compose.yml", "Docker Compose", False),
    ]
    
    for filepath, desc, required in files_to_check:
        if not check_file(filepath, desc, required) and required:
            all_ok = False
    
    # Проверка .env файла
    print(f"\n⚙️ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ:")
    env_vars = parse_env_file()
    
    # Объединяем переменные из файла и системы
    for key, value in env_vars.items():
        os.environ[key] = value
    
    env_checks = [
        ("TELEGRAM_BOT_TOKEN", "Токен Telegram бота", True),
        ("UPDATES_CHANNEL_ID", "ID канала обновлений", False),
        ("FULL_CHANNEL_ID", "ID канала полного отчета", False),
        ("TELEGRAM_UPDATES_CHANNEL_ID", "ID канала обновлений (старое)", False),
        ("TELEGRAM_FULL_CHANNEL_ID", "ID канала полного отчета (старое)", False),
    ]
    
    has_channel_config = False
    for var_name, desc, required in env_checks:
        if check_env_var(var_name, desc, required):
            if "CHANNEL" in var_name:
                has_channel_config = True
        elif required:
            all_ok = False
    
    if not has_channel_config:
        print("⚠️ Не найдена конфигурация каналов")
        all_ok = False
    
    # Проверка Python пакетов
    print(f"\n📦 PYTHON ПАКЕТЫ:")
    try:
        import aiogram
        print(f"✅ aiogram: {aiogram.__version__}")
    except ImportError:
        print("❌ aiogram: не установлен")
        all_ok = False
    
    try:
        import aiohttp
        print(f"✅ aiohttp: {aiohttp.__version__}")
    except ImportError:
        print("❌ aiohttp: не установлен")
        all_ok = False
    
    try:
        import pydantic
        print(f"✅ pydantic: {pydantic.__version__}")
    except ImportError:
        print("❌ pydantic: не установлен")
        all_ok = False
    
    # Проверка директорий
    print(f"\n📂 ДИРЕКТОРИИ:")
    dirs_to_check = [
        ("logs", "Логи", False),
        ("roblox_garden", "Основной пакет", True),
        ("roblox_garden/core", "Ядро системы", True),
        ("roblox_garden/telegram", "Telegram интеграция", True),
    ]
    
    for dirpath, desc, required in dirs_to_check:
        exists = os.path.isdir(dirpath)
        status = "✅" if exists else ("❌" if required else "⚠️")
        print(f"{status} {desc}: {dirpath}")
        if not exists and required:
            all_ok = False
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    
    if not os.path.exists('.env'):
        print("📝 Создайте .env файл с помощью: python get_channel_ids.py")
    
    if not has_channel_config:
        print("📱 Настройте каналы Telegram: python get_channel_ids.py")
    
    if not os.path.exists('logs'):
        print("📁 Создайте директорию logs: mkdir logs")
    
    # Следующие шаги
    print(f"\n🚀 СЛЕДУЮЩИЕ ШАГИ:")
    
    if all_ok:
        print("✅ Система готова к запуску!")
        print("🎯 Запустите бота: python -m roblox_garden")
        print("🐳 Или через Docker: ./deploy.sh")
    else:
        print("❌ Система НЕ готова к запуску")
        print("🔧 Исправьте ошибки выше")
        
        if not has_channel_config:
            print("1. Настройте каналы: python get_channel_ids.py")
        
        print("2. Установите зависимости: pip install -r requirements.txt")
        print("3. Проверьте снова: python check_setup.py")
    
    # Полезные команды
    print(f"\n📋 ПОЛЕЗНЫЕ КОМАНДЫ:")
    print("🔍 Настройка каналов:     python get_channel_ids.py")
    print("📊 Демо без Telegram:     python demo.py")
    print("🔧 Тест Telegram:         python test_telegram.py")
    print("🐳 Docker развертывание:  ./deploy.sh")
    print("📖 Полный обзор:          python overview.py")
    
    return all_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Проверка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка при проверке: {e}")
        sys.exit(1)
