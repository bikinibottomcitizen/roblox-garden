# Roblox Garden WebSocket Parser

Современный Python парсер для мониторинга магазина игры Roblox Garden с интеграцией Telegram бота.

## 🚀 Быстрый старт

### 1. Автоматическая настройка каналов
```bash
python get_channel_ids.py
```
Скрипт автоматически найдет ID ваших Telegram каналов и создаст `.env` файл.

### 2. Запуск бота
```bash
python -m roblox_garden
```

### 3. Docker развертывание
```bash
./deploy.sh
```

## Возможности

- 🔄 Мониторинг API Roblox Garden в реальном времени
- 📊 Данные о редкости предметов с growagardenpro.com
- 📱 Интеграция с Telegram ботом
- 🎯 Умная фильтрация по редкости предметов
- 📊 Два канала: полные обновления + только новые предметы
- ⚙️ Конфигурируемые фильтры
- 🏗️ Современная асинхронная архитектура
- 🐳 Готовая Docker инфраструктура

## Фильтры

### Семена и Гиры
- **Редкость**: Divine и выше
- **Исключения**: Harvest Tool, Favorite Tool, Cleaning Spray

### Яйца
Только следующие типы:
- Bee Egg
- Paradise Egg  
- Bug Egg
- Mythical Egg

## Установка

```bash
# Клонирование репозитория
git clone <repository-url>
cd roblox-garden

# Установка зависимостей
pip install -e .

# Для разработки
pip install -e ".[dev]"
```

## Настройка

### Автоматическая (рекомендуется)

Используйте скрипт для автоматического определения ID каналов:

```bash
python get_channel_ids.py
```

Скрипт:
- 🤖 Проверит токен вашего бота
- 📢 Найдет все доступные каналы
- 🔧 Покажет права бота в каждом канале
- 📁 Создаст `.env` файл с настройками

### Ручная настройка

1. Создайте файл `.env` в корне проекта:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_FULL_CHANNEL_ID=-1001234567890
TELEGRAM_UPDATES_CHANNEL_ID=-1001234567891

# API Configuration
ROBLOX_API_BASE_URL=https://gagapi.onrender.com
API_POLL_INTERVAL=30
FULL_REPORT_INTERVAL=300

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/roblox_garden.log
```

2. Настройте Telegram бота:
   - Создайте бота через @BotFather
   - Добавьте бота в каналы как администратора
   - Получите ID каналов (используйте `python get_channel_ids.py`)

## Запуск

### Локальный запуск
```bash
# Настройка каналов (один раз)
python get_channel_ids.py

# Запуск основного приложения
python -m roblox_garden

# Демонстрация работы парсера
python demo.py
```

### Docker развертывание
```bash
# Разработка
./deploy.sh

# Продакшн с Docker Secrets
./deploy-prod.sh
```

## Полезные скрипты

| Скрипт | Описание |
|--------|----------|
| `get_channel_ids.py` | 🔍 Автоматическое определение ID каналов Telegram |
| `demo_channel_ids.py` | 🎯 Демонстрация работы скрипта настройки каналов |
| `demo.py` | 📊 Демонстрация парсера без Telegram |
| `test_telegram.py` | 🔧 Тестирование Telegram бота |
| `debug_api.py` | 🐛 Отладка API данных |

## Архитектура

```
roblox_garden/
├── core/           # Основная логика приложения
├── models/         # Модели данных (Pydantic)
├── filters/        # Фильтры предметов по редкости
├── telegram/       # Telegram бот интеграция
├── websocket/      # HTTP клиент для API
├── utils/          # Утилиты и форматирование
└── config/         # Конфигурация и настройки
```

## Демонстрация работы

Для тестирования парсера запустите демо скрипт:

```bash
python demo.py
```

Пример вывода:
```
🔍 Подключение к Roblox Garden API...
✅ Получено 33 предметов из API
✨ Найдено 4 подходящих предметов:
🌱 [Mythical] Cactus (5шт)
⚙️ [Divine] Master Sprinkler (1шт)
🌱 [Divine] Hive Fruit (1шт)
🌱 [Mythical] Nectarine (1шт)
```

## Структура сообщений

### Канал обновлений (новые предметы)
```
🌱[Divine] Giant Pinecone в стоке
🛒 Доступно для покупки
---
```

### Канал полного отчета (каждые 5 минут)
```
📋 Полный отчет о стоке
🕐 Время: 04:34

🌱 Seeds:
  ✨ Beanstalk (1шт) (Divine)
    ✅ В наличии

📊 Статистика:
📦 Всего товаров: 19
✅ В наличии: 19
```

## Разработка

```bash
# Форматирование кода
black .

# Проверка типов
mypy roblox_garden

# Тестирование
pytest

# Pre-commit хуки
pre-commit install
```

## 📚 Документация

- **[CHANNEL_SETUP.md](CHANNEL_SETUP.md)** - Подробная инструкция по настройке каналов
- **[DOCKER.md](DOCKER.md)** - Руководство по Docker развертыванию
- **[SETUP.md](SETUP.md)** - Общее руководство по установке

## 🔧 Разработка

```bash
# Установка dev зависимостей
pip install -e ".[dev]"

# Запуск тестов
python -m pytest

# Линтинг
python -m pylint roblox_garden/
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add some amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📜 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для получения дополнительной информации.
