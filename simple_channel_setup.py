#!/usr/bin/env python3

"""
Простой скрипт для настройки каналов Telegram.
Ручной ввод ID каналов для Roblox Garden Bot.
"""

import os
import re


def update_env_file(full_channel_id: str, updates_channel_id: str, bot_token: str | None = None):
    """Обновить файл .env с ID каналов."""
    
    # Читаем существующий .env или создаем новый
    env_lines = []
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            env_lines = f.readlines()
    
    # Обновляем/добавляем значения
    updated_lines = []
    bot_token_found = False
    full_channel_found = False
    updates_channel_found = False
    
    for line in env_lines:
        line = line.strip()
        if line.startswith('TELEGRAM_BOT_TOKEN='):
            if bot_token:
                updated_lines.append(f'TELEGRAM_BOT_TOKEN={bot_token}\n')
            else:
                updated_lines.append(line + '\n')
            bot_token_found = True
        elif line.startswith('TELEGRAM_FULL_CHANNEL_ID='):
            updated_lines.append(f'TELEGRAM_FULL_CHANNEL_ID={full_channel_id}\n')
            full_channel_found = True
        elif line.startswith('TELEGRAM_UPDATES_CHANNEL_ID='):
            updated_lines.append(f'TELEGRAM_UPDATES_CHANNEL_ID={updates_channel_id}\n')
            updates_channel_found = True
        else:
            updated_lines.append(line + '\n')
    
    # Добавляем недостающие параметры
    if bot_token and not bot_token_found:
        updated_lines.insert(0, f'TELEGRAM_BOT_TOKEN={bot_token}\n')
    if not full_channel_found:
        updated_lines.append(f'TELEGRAM_FULL_CHANNEL_ID={full_channel_id}\n')
    if not updates_channel_found:
        updated_lines.append(f'TELEGRAM_UPDATES_CHANNEL_ID={updates_channel_id}\n')
    
    # Записываем файл
    with open('.env', 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)


def main():
    """Главная функция."""
    print("🤖 ПРОСТАЯ НАСТРОЙКА КАНАЛОВ TELEGRAM")
    print("=" * 50)
    print()
    print("📋 Инструкция по получению ID каналов:")
    print("1. Откройте Telegram Web (web.telegram.org)")
    print("2. Перейдите в ваш канал")
    print("3. Скопируйте числа из URL после 'c/' (например: 1234567890)")
    print("4. Добавьте -100 в начало (получится: -1001234567890)")
    print()
    print("🔧 Убедитесь что бот добавлен в каналы как администратор!")
    print()
    
    # Проверить токен бота в .env
    bot_token = None
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('TELEGRAM_BOT_TOKEN='):
                    bot_token = line.split('=', 1)[1].strip()
                    break
    
    if not bot_token or bot_token == 'your_bot_token_here':
        print("❌ Токен бота не найден в .env")
        while True:
            bot_token = input("🔑 Введите токен бота: ").strip()
            if bot_token and re.match(r'^\d+:.+', bot_token):
                break
            print("❌ Неверный формат токена! Должен быть вида: 1234567890:ABC...")
    else:
        print(f"✅ Токен бота найден в .env")
    
    # Ввод ID полного канала
    while True:
        full_channel = input("\n📺 ID полного канала (например: -1001234567890): ").strip()
        
        if not full_channel:
            print("❌ ID канала не может быть пустым!")
            continue
        
        # Автоматически добавляем -100 если нужно
        if full_channel.isdigit():
            full_channel = f"-100{full_channel}"
        elif not full_channel.startswith('-100'):
            print("❌ ID канала должен начинаться с -100 или быть числом")
            continue
        
        break
    
    # Ввод ID канала обновлений
    while True:
        updates_channel = input("📱 ID канала обновлений (например: -1001234567891): ").strip()
        
        if not updates_channel:
            print("❌ ID канала не может быть пустым!")
            continue
        
        # Автоматически добавляем -100 если нужно
        if updates_channel.isdigit():
            updates_channel = f"-100{updates_channel}"
        elif not updates_channel.startswith('-100'):
            print("❌ ID канала должен начинаться с -100 или быть числом")
            continue
        
        break
    
    # Сохранить в .env
    try:
        update_env_file(full_channel, updates_channel, bot_token)
        print("\n✅ Конфигурация сохранена в .env!")
        print(f"   Полный канал: {full_channel}")
        print(f"   Канал обновлений: {updates_channel}")
        print("\n🚀 Теперь можно запускать бота!")
        
    except Exception as e:
        print(f"\n❌ Ошибка сохранения: {e}")
        print("Добавьте эти строки в .env вручную:")
        print(f"TELEGRAM_FULL_CHANNEL_ID={full_channel}")
        print(f"TELEGRAM_UPDATES_CHANNEL_ID={updates_channel}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Настройка отменена")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
