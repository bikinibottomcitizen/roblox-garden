#!/usr/bin/env python3

"""
Скрипт для определения ID каналов Telegram.
Помогает найти ID каналов для настройки Roblox Garden Bot.
"""

import asyncio
import os
import sys
from typing import Optional, List, Dict, Any

try:
    from aiogram import Bot, Dispatcher
    from aiogram.types import Update, Chat, Message
    from aiogram.exceptions import TelegramBadRequest, TelegramUnauthorizedError
    import aiohttp
except ImportError as e:
    print("❌ Ошибка импорта:", e)
    print("📦 Установите зависимости: pip install aiogram aiohttp")
    sys.exit(1)


class ChannelIdFinder:
    """Класс для поиска ID каналов Telegram."""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.bot = Bot(token=bot_token)
    
    async def get_bot_info(self) -> Optional[Dict[str, Any]]:
        """Получить информацию о боте."""
        try:
            bot_info = await self.bot.get_me()
            return {
                'id': bot_info.id,
                'username': bot_info.username,
                'first_name': bot_info.first_name,
                'can_join_groups': bot_info.can_join_groups,
                'can_read_all_group_messages': bot_info.can_read_all_group_messages
            }
        except Exception as e:
            print(f"❌ Ошибка получения информации о боте: {e}")
            return None
    
    async def get_updates(self) -> List[Update]:
        """Получить последние обновления."""
        try:
            updates = await self.bot.get_updates(limit=100, timeout=1)
            return updates
        except Exception as e:
            print(f"❌ Ошибка получения обновлений: {e}")
            return []
    
    async def analyze_chat(self, chat: Chat) -> Dict[str, Any]:
        """Анализировать информацию о чате."""
        try:
            # Получить количество участников
            member_count = None
            if chat.type in ['group', 'supergroup', 'channel']:
                try:
                    member_count = await self.bot.get_chat_member_count(chat.id)
                except:
                    member_count = "Неизвестно"
            
            # Получить информацию о боте в чате
            bot_member = None
            bot_can_post = False
            try:
                bot_info = await self.bot.get_me()
                bot_member = await self.bot.get_chat_member(chat.id, bot_info.id)
                
                # Проверить права на отправку сообщений
                if bot_member:
                    if bot_member.status in ['administrator', 'creator']:
                        # Для администраторов проверяем конкретные права
                        if hasattr(bot_member, 'can_post_messages'):
                            bot_can_post = getattr(bot_member, 'can_post_messages', True)
                        else:
                            bot_can_post = True  # По умолчанию админы могут писать
                    elif bot_member.status == 'member':
                        bot_can_post = True  # Обычные участники могут писать
            except:
                pass
            
            return {
                'id': chat.id,
                'type': chat.type,
                'title': chat.title,
                'username': chat.username,
                'description': chat.description,
                'member_count': member_count,
                'bot_status': bot_member.status if bot_member else "Не участник",
                'bot_can_post': bot_can_post
            }
        except Exception as e:
            return {
                'id': chat.id,
                'type': chat.type,
                'title': chat.title or "Без названия",
                'username': chat.username,
                'error': str(e)
            }
    
    async def find_channels(self) -> Dict[str, List[Dict[str, Any]]]:
        """Найти все каналы и группы, где есть бот."""
        print("🔍 Поиск каналов...")
        
        # Получить обновления
        updates = await self.get_updates()
        
        if not updates:
            print("⚠️ Нет последних сообщений. Отправьте боту сообщение или добавьте в каналы.")
            return {'channels': [], 'groups': [], 'private': []}
        
        # Собрать уникальные чаты
        chats = {}
        for update in updates:
            if update.message and update.message.chat:
                chat = update.message.chat
                chats[chat.id] = chat
            elif update.channel_post and update.channel_post.chat:
                chat = update.channel_post.chat
                chats[chat.id] = chat
        
        # Анализировать каждый чат
        channels = []
        groups = []
        private = []
        
        for chat in chats.values():
            chat_info = await self.analyze_chat(chat)
            
            if chat.type == 'channel':
                channels.append(chat_info)
            elif chat.type in ['group', 'supergroup']:
                groups.append(chat_info)
            elif chat.type == 'private':
                private.append(chat_info)
        
        return {
            'channels': channels,
            'groups': groups,
            'private': private
        }
    
    async def test_channel_access(self, channel_id: str) -> Dict[str, Any]:
        """Проверить доступ к каналу."""
        try:
            chat = await self.bot.get_chat(channel_id)
            
            # Проверить может ли бот отправлять сообщения
            can_send = False
            try:
                bot_info = await self.bot.get_me()
                member = await self.bot.get_chat_member(channel_id, bot_info.id)
                
                if member:
                    if member.status in ['administrator', 'creator']:
                        # Для администраторов проверяем права
                        if hasattr(member, 'can_post_messages'):
                            can_send = getattr(member, 'can_post_messages', True)
                        else:
                            can_send = True  # По умолчанию админы могут писать
                    elif member.status == 'member':
                        can_send = True  # Обычные участники могут писать
            except:
                pass
            
            return {
                'accessible': True,
                'chat_info': await self.analyze_chat(chat),
                'can_send_messages': can_send
            }
        except Exception as e:
            return {
                'accessible': False,
                'error': str(e)
            }
    
    async def close(self):
        """Закрыть соединение."""
        await self.bot.session.close()


def print_chat_info(chat_info: Dict[str, Any], index: int):
    """Красиво вывести информацию о чате."""
    print(f"\n{index}. 📢 {chat_info.get('title', 'Без названия')}")
    print(f"   🆔 ID: {chat_info['id']}")
    print(f"   📱 Тип: {chat_info['type']}")
    
    if chat_info.get('username'):
        print(f"   🔗 Username: @{chat_info['username']}")
    
    if chat_info.get('member_count'):
        print(f"   👥 Участников: {chat_info['member_count']}")
    
    print(f"   🤖 Статус бота: {chat_info.get('bot_status', 'Неизвестно')}")
    
    if chat_info.get('bot_can_post'):
        print(f"   ✅ Может отправлять сообщения")
    elif chat_info.get('bot_status') == 'administrator':
        print(f"   ⚠️ Администратор, но нет прав на отправку")
    else:
        print(f"   ❌ Не может отправлять сообщения")


async def interactive_setup(finder: ChannelIdFinder):
    """Интерактивная настройка каналов."""
    print("\n🎯 ИНТЕРАКТИВНАЯ НАСТРОЙКА КАНАЛОВ")
    print("=" * 50)
    
    # Найти все каналы
    chats = await finder.find_channels()
    
    all_chats = []
    
    # Показать каналы
    if chats['channels']:
        print(f"\n📺 НАЙДЕННЫЕ КАНАЛЫ ({len(chats['channels'])})")
        print("-" * 30)
        for i, channel in enumerate(chats['channels'], 1):
            print_chat_info(channel, i)
            all_chats.append(('channel', channel))
    
    # Показать группы/супергруппы
    if chats['groups']:
        print(f"\n👥 НАЙДЕННЫЕ ГРУППЫ ({len(chats['groups'])})")
        print("-" * 30)
        start_index = len(all_chats) + 1
        for i, group in enumerate(chats['groups'], start_index):
            print_chat_info(group, i)
            all_chats.append(('group', group))
    
    if not all_chats:
        print("\n❌ Каналы не найдены!")
        print("\n📋 Что нужно сделать:")
        print("1. Добавьте бота в ваши каналы как администратора")
        print("2. Дайте боту права на отправку сообщений")
        print("3. Отправьте любое сообщение в канал")
        print("4. Запустите этот скрипт снова")
        return None, None
    
    print(f"\n🔧 НАСТРОЙКА КАНАЛОВ")
    print("-" * 20)
    
    # Выбор канала для обновлений
    updates_channel = None
    while not updates_channel:
        try:
            print(f"\n📱 Выберите канал для ОБНОВЛЕНИЙ (1-{len(all_chats)}):")
            choice = input("Введите номер: ").strip()
            
            if choice.lower() in ['q', 'quit', 'exit']:
                return None, None
            
            index = int(choice) - 1
            if 0 <= index < len(all_chats):
                updates_channel = all_chats[index][1]
                print(f"✅ Канал обновлений: {updates_channel['title']} (ID: {updates_channel['id']})")
            else:
                print("❌ Неверный номер. Попробуйте снова.")
        except ValueError:
            print("❌ Введите число от 1 до", len(all_chats))
        except KeyboardInterrupt:
            return None, None
    
    # Выбор канала для полного отчета
    full_channel = None
    while not full_channel:
        try:
            print(f"\n📊 Выберите канал для ПОЛНОГО ОТЧЕТА (1-{len(all_chats)}):")
            print("(Можно выбрать тот же канал, что и для обновлений)")
            choice = input("Введите номер: ").strip()
            
            if choice.lower() in ['q', 'quit', 'exit']:
                return None, None
            
            index = int(choice) - 1
            if 0 <= index < len(all_chats):
                full_channel = all_chats[index][1]
                print(f"✅ Канал полного отчета: {full_channel['title']} (ID: {full_channel['id']})")
            else:
                print("❌ Неверный номер. Попробуйте снова.")
        except ValueError:
            print("❌ Введите число от 1 до", len(all_chats))
        except KeyboardInterrupt:
            return None, None
    
    return updates_channel, full_channel


def generate_env_config(bot_token: str, updates_channel: Dict[str, Any], full_channel: Dict[str, Any]):
    """Сгенерировать конфигурацию для .env файла."""
    print(f"\n🎉 КОНФИГУРАЦИЯ ГОТОВА!")
    print("=" * 50)
    
    print(f"\n📝 Добавьте эти строки в ваш .env файл:")
    print("-" * 40)
    print(f"TELEGRAM_BOT_TOKEN={bot_token}")
    print(f"UPDATES_CHANNEL_ID={updates_channel['id']}")
    print(f"FULL_CHANNEL_ID={full_channel['id']}")
    
    print(f"\n📋 Информация о каналах:")
    print(f"📱 Канал обновлений: {updates_channel['title']} (ID: {updates_channel['id']})")
    print(f"📊 Канал полного отчета: {full_channel['title']} (ID: {full_channel['id']})")
    
    # Создать .env файл
    env_content = f"""# Roblox Garden Bot Configuration
# Сгенерировано автоматически {asyncio.get_event_loop().time()}

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={bot_token}
UPDATES_CHANNEL_ID={updates_channel['id']}
FULL_CHANNEL_ID={full_channel['id']}

# Альтернативные названия (для обратной совместимости)
TELEGRAM_UPDATES_CHANNEL_ID={updates_channel['id']}
TELEGRAM_FULL_CHANNEL_ID={full_channel['id']}

# WebSocket Configuration
WS_URL=wss://api.growagarden.com/socket
RECONNECT_DELAY=5
MAX_RECONNECT_ATTEMPTS=10

# Update Intervals (in seconds)
UPDATE_INTERVAL=300        # 5 minutes
FULL_UPDATE_INTERVAL=300   # 5 minutes

# Timezone
TIMEZONE=Europe/Moscow

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/roblox_garden.log
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"\n✅ Файл .env создан/обновлен!")
    except Exception as e:
        print(f"\n⚠️ Не удалось создать .env файл: {e}")
        print("Скопируйте конфигурацию вручную.")


async def manual_check():
    """Ручная проверка ID канала."""
    print(f"\n🔍 РУЧНАЯ ПРОВЕРКА КАНАЛА")
    print("-" * 30)
    
    bot_token = input("Введите токен бота: ").strip()
    if not bot_token:
        print("❌ Токен не может быть пустым")
        return
    
    channel_id = input("Введите ID канала (например, -1001234567890): ").strip()
    if not channel_id:
        print("❌ ID канала не может быть пустым")
        return
    
    finder = ChannelIdFinder(bot_token)
    
    try:
        print(f"\n🔍 Проверка канала {channel_id}...")
        result = await finder.test_channel_access(channel_id)
        
        if result['accessible']:
            print("✅ Канал доступен!")
            print_chat_info(result['chat_info'], 1)
            
            if result['can_send_messages']:
                print("✅ Бот может отправлять сообщения в этот канал")
            else:
                print("❌ Бот НЕ может отправлять сообщения в этот канал")
                print("💡 Убедитесь, что бот - администратор с правами на отправку сообщений")
        else:
            print("❌ Канал недоступен!")
            print(f"Ошибка: {result['error']}")
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
    finally:
        await finder.close()


async def main():
    """Главная функция."""
    print("🤖 ОПРЕДЕЛЕНИЕ ID КАНАЛОВ TELEGRAM")
    print("=" * 50)
    print("Этот скрипт поможет найти ID каналов для Roblox Garden Bot")
    
    # Проверить существующий .env файл
    if os.path.exists('.env'):
        print("\n⚠️ Файл .env уже существует")
        overwrite = input("Перезаписать его? (y/N): ").strip().lower()
        if overwrite not in ['y', 'yes', 'да']:
            print("Операция отменена")
            return
    
    print(f"\n📋 Что нужно для работы:")
    print("1. 🤖 Токен вашего Telegram бота (@BotFather)")
    print("2. 📢 Бот должен быть добавлен в каналы как администратор")
    print("3. 🔧 У бота должны быть права на отправку сообщений")
    print("4. 💬 В каналах должно быть хотя бы одно сообщение")
    
    while True:
        print(f"\n🔧 Выберите режим:")
        print("1. 🎯 Автоматический поиск каналов (рекомендуется)")
        print("2. 🔍 Ручная проверка ID канала")
        print("3. ❌ Выход")
        
        choice = input("Ваш выбор (1-3): ").strip()
        
        if choice == '1':
            # Автоматический режим
            bot_token = input("\n🤖 Введите токен бота: ").strip()
            
            if not bot_token:
                print("❌ Токен не может быть пустым")
                continue
            
            finder = ChannelIdFinder(bot_token)
            
            try:
                # Проверить токен
                print("\n🔍 Проверка токена...")
                bot_info = await finder.get_bot_info()
                
                if not bot_info:
                    print("❌ Неверный токен бота!")
                    continue
                
                print(f"✅ Бот найден: @{bot_info['username']} ({bot_info['first_name']})")
                
                # Интерактивная настройка
                updates_channel, full_channel = await interactive_setup(finder)
                
                if updates_channel and full_channel:
                    generate_env_config(bot_token, updates_channel, full_channel)
                    
                    print(f"\n🚀 Готово! Теперь можете запустить бота:")
                    print("python -m roblox_garden")
                    print("или")
                    print("./deploy.sh")
                    break
                else:
                    print("Настройка отменена")
            
            except TelegramUnauthorizedError:
                print("❌ Неверный токен бота!")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
            finally:
                await finder.close()
        
        elif choice == '2':
            # Ручной режим
            await manual_check()
        
        elif choice == '3':
            print("👋 До свидания!")
            break
        
        else:
            print("❌ Неверный выбор")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Операция прервана пользователем")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)
