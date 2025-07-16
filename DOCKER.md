# Roblox Garden Bot - Docker Deployment

Этот документ описывает как развернуть Roblox Garden Bot в Docker контейнере.

## 🚀 Быстрый старт

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/bikinibottomcitizen/roblox-garden.git
   cd roblox-garden
   ```

2. **Настройте переменные окружения**:
   ```bash
   cp .env.example .env
   # Отредактируйте .env файл своими настройками
   ```

3. **Запустите развертывание**:
   ```bash
   ./deploy.sh
   ```

## ⚙️ Конфигурация

### Обязательные настройки

В файле `.env` укажите:

- `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота
- `UPDATES_CHANNEL_ID` - ID канала для обновлений  
- `FULL_CHANNEL_ID` - ID канала для полных отчетов

### Получение токена бота

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен и укажите в `TELEGRAM_BOT_TOKEN`
3. Добавьте бота в каналы как администратора
4. Получите ID каналов через [@userinfobot](https://t.me/userinfobot)

### Дополнительные настройки

```bash
# WebSocket подключение
WS_URL=wss://api.growagarden.com/socket
RECONNECT_DELAY=5
MAX_RECONNECT_ATTEMPTS=10

# Интервалы обновлений (в секундах)
UPDATE_INTERVAL=300
FULL_UPDATE_INTERVAL=300

# Часовой пояс
TIMEZONE=Europe/Moscow

# Логирование
LOG_LEVEL=INFO
LOG_FILE=logs/roblox_garden.log
```

## 🐳 Docker команды

### Основные команды

```bash
# Запуск в фоне
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Пересборка образа
docker-compose build --no-cache
```

### Управление

```bash
# Проверка статуса
docker-compose ps

# Вход в контейнер
docker-compose exec roblox-garden bash

# Просмотр использования ресурсов
docker stats
```

## 📊 Мониторинг

### Логи

Логи сохраняются в папку `logs/` и доступны через:

```bash
# Живые логи
docker-compose logs -f

# Последние 100 строк
docker-compose logs --tail=100

# Логи за последний час
docker-compose logs --since=1h
```

### Health Check

Контейнер имеет встроенную проверку здоровья:

```bash
# Проверка состояния
docker-compose ps
```

### Ресурсы

Лимиты ресурсов:
- **Memory**: 256MB (лимит), 128MB (резерв)
- **CPU**: 0.5 ядра (лимит), 0.25 ядра (резерв)

## 🔧 Производственное развертывание

### Systemd сервис

Создайте systemd сервис для автозапуска:

```bash
sudo nano /etc/systemd/system/roblox-garden.service
```

```ini
[Unit]
Description=Roblox Garden Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/roblox-garden
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable roblox-garden
sudo systemctl start roblox-garden
```

### Nginx прокси (опционально)

Если нужен веб-интерфейс:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🛠️ Разработка

### Локальная разработка

```bash
# Запуск без Docker
python -m roblox_garden

# Тестирование
python test_updated_system.py
```

### Отладка

```bash
# Запуск с отладочными логами
LOG_LEVEL=DEBUG docker-compose up

# Интерактивный режим
docker-compose run --rm roblox-garden bash
```

## 📝 Структура проекта

```
roblox-garden/
├── Dockerfile              # Образ приложения
├── docker-compose.yml      # Композиция сервисов
├── .dockerignore           # Исключения для сборки
├── .env.example            # Пример конфигурации
├── deploy.sh               # Скрипт развертывания
├── requirements.txt        # Python зависимости
├── logs/                   # Логи приложения
└── roblox_garden/          # Исходный код
    ├── __main__.py
    ├── config/
    ├── core/
    ├── filters/
    ├── models/
    ├── telegram/
    ├── utils/
    └── websocket/
```

## 🆘 Устранение неполадок

### Типичные проблемы

1. **Контейнер не запускается**:
   ```bash
   docker-compose logs
   # Проверьте конфигурацию в .env
   ```

2. **Бот не отправляет сообщения**:
   - Проверьте токен бота
   - Убедитесь что бот добавлен в каналы
   - Проверьте права администратора

3. **Нет подключения к WebSocket**:
   ```bash
   # Проверьте сетевое подключение
   docker-compose exec roblox-garden ping api.growagarden.com
   ```

### Получение помощи

1. Просмотрите логи: `docker-compose logs -f`
2. Проверьте статус: `docker-compose ps`
3. Проверьте конфигурацию: `cat .env`

## 🔐 Безопасность

- Храните `.env` файл в безопасности
- Не коммитьте токены в Git
- Используйте Docker Secrets в продакшене
- Регулярно обновляйте образы
