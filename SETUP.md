# Инструкция по запуску Roblox Garden Parser

## Быстрый старт

### 1. Настройка Telegram бота

1. Создайте бота через [@BotFather](https://t.me/BotFather):
   - Отправьте `/newbot`
   - Следуйте инструкциям
   - Сохраните токен бота

2. Создайте два канала в Telegram:
   - Канал для полных отчетов (каждые 5 минут)
   - Канал для обновлений (только новые предметы)

3. Добавьте бота в каналы как администратора

4. Получите ID каналов:
   - Добавьте бота [@userinfobot](https://t.me/userinfobot) в каналы
   - Или используйте бота [@get_id_bot](https://t.me/get_id_bot)

### 2. Настройка проекта

1. Отредактируйте файл `.env`:
```bash
cp .env.example .env
# Отредактируйте .env и укажите ваши данные
```

2. Заполните обязательные поля в `.env`:
```env
TELEGRAM_BOT_TOKEN=ваш_токен_бота
TELEGRAM_FULL_CHANNEL_ID=-1001234567890
TELEGRAM_UPDATES_CHANNEL_ID=-1001234567891
```

### 3. Запуск

```bash
# Установка зависимостей (уже выполнено)
pip install -r requirements.txt

# Запуск приложения
python -m roblox_garden

# Запуск в режиме отладки
python -m roblox_garden --debug
```

## Структура проекта

```
roblox_garden/
├── core/              # Основная логика приложения
├── models/            # Модели данных (предметы, магазин)
├── filters/           # Фильтры предметов по правилам
├── telegram/          # Интеграция с Telegram
├── websocket/         # WebSocket клиент для API
├── utils/             # Утилиты форматирования
└── config/            # Конфигурация и настройки
```

## Что делает приложение

1. **Подключается к API** Roblox Garden для получения данных магазина
2. **Фильтрует предметы** по заданным правилам:
   - Семена и гиры: редкость Divine и выше
   - Исключает: Harvest Tool, Favorite Tool, Cleaning Spray
   - Яйца: только Bee Egg, Paradise Egg, Bug Egg, Mythical Egg
3. **Отправляет в Telegram**:
   - **Канал обновлений**: новые предметы в реальном времени
   - **Канал отчетов**: полный отчет каждые 5 минут

## Примеры сообщений

### Канал обновлений
```
🌱[Divine] Giant Pinecone в стоке
🛒 Доступно для покупки
---
⚙️[Divine] Master Sprinkler в стоке
🛒 Доступно для покупки
```

### Канал полных отчетов
```
📋 Полный отчет о стоке
🕐 Время: 04:34

🌱 Seeds:
  ✨ Beanstalk (1шт) (Divine)
    ✅ В наличии

⚙️ Gears:
  ✨ Master Sprinkler (1шт) (Divine)
    ✅ В наличии

🥚 Eggs:
  🔴 Paradise Egg (1шт) (Mythical)
    ✅ В наличии

📊 Статистика:
📦 Всего товаров: 3
✅ В наличии: 3
❌ Отсутствует: 0
```

## Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск только тестов фильтров
pytest tests/test_filters.py -v

# Демонстрация фильтрации
python -c "
from roblox_garden.filters.item_filters import RobloxGardenFilter
print('Фильтры работают!')
"
```

## Настройки

Все настройки находятся в файле `.env`:

- `SHOP_UPDATE_INTERVAL=300` - интервал полных отчетов (секунды)
- `WEBSOCKET_RECONNECT_DELAY=5` - задержка переподключения
- `LOG_LEVEL=INFO` - уровень логирования
- `TIMEZONE=Europe/Moscow` - часовой пояс для времени

## Решение проблем

1. **Ошибки с Telegram**: проверьте токен и ID каналов
2. **Нет данных**: проверьте доступность API Roblox Garden
3. **Ошибки подключения**: проверьте интернет-соединение

## API Reference

Приложение использует API: https://gagapi.onrender.com/

Структура данных соответствует репозиторию: https://github.com/Liriosha/GAGAPI/
