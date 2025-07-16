# 🚀 Быстрый деплой на VPS - Пошаговая инструкция

## 📦 Подготовка архива (на локальной машине)

```bash
# Создание архива для VPS
./pack-for-vps.sh
```

Это создаст архив `roblox-garden-vps-YYYYMMDD-HHMMSS.tar.gz` со всеми необходимыми файлами.

## 🖥️ Деплой на VPS

### 1. Загрузка на VPS
```bash
# Загрузите архив на VPS любым способом (scp, wget, etc.)
scp roblox-garden-vps-*.tar.gz user@your-vps-ip:~/

# Подключитесь к VPS
ssh user@your-vps-ip
```

### 2. Распаковка и настройка
```bash
# Распаковка архива
tar -xzf roblox-garden-vps-*.tar.gz
cd roblox-garden

# Первичная настройка VPS (установка Docker, etc.)
# Можно запускать как от root, так и от обычного пользователя
./vps-setup.sh

# При запуске от root будет предложено создать пароль для docker-user
# Или можно установить пароль через переменную окружения:
# DOCKER_USER_PASSWORD="your_secure_password" ./vps-setup.sh

# Перезагрузка (необходимо для применения прав Docker)
sudo reboot  # или просто reboot если запускали от root
```

### 3. Деплой приложения
```bash
# После перезагрузки
cd roblox-garden

# Запуск деплоя (можно от root или обычного пользователя)
./deploy-vps.sh

# Если настройка выполнялась от root, то можно переключиться на docker-user:
# su - docker-user
# cd /home/docker-user/roblox-garden
# ./deploy-vps.sh
```

Скрипт запросит:
- **Telegram Bot Token** (получить у @BotFather)
- **Updates Channel ID** (например: -1001234567890)
- **Full Report Channel ID** (например: -1001234567891)

### 4. Проверка работы
```bash
# Статус контейнеров
docker-compose -f docker-compose.vps.yml ps

# Просмотр логов
docker-compose -f docker-compose.vps.yml logs -f

# Проверка здоровья
docker stats roblox-garden-prod
```

## 🔧 Управление сервисом

### Базовые команды
```bash
# Остановка
docker-compose -f docker-compose.vps.yml down

# Запуск
docker-compose -f docker-compose.vps.yml up -d

# Перезапуск
docker-compose -f docker-compose.vps.yml restart

# Просмотр логов в реальном времени
docker-compose -f docker-compose.vps.yml logs -f
```

### Полезные алиасы (создаются автоматически)
```bash
rg-logs     # Просмотр логов
rg-status   # Статус сервиса
rg-restart  # Перезапуск
rg-stop     # Остановка
rg-start    # Запуск
rg-update   # Обновление из git
```

## 🔒 Безопасность

### Файлы с секретами (создаются автоматически)
- `secrets/telegram_bot_token.txt` - Токен бота
- `secrets/updates_channel_id.txt` - ID канала обновлений
- `secrets/full_channel_id.txt` - ID канала полных отчетов

Все файлы имеют права доступа 600 (только владелец).

### Резервное копирование
```bash
# Создание бэкапа секретов
tar -czf secrets_backup_$(date +%Y%m%d).tar.gz secrets/
```

## 📊 Мониторинг

### Автозапуск при перезагрузке
Systemd сервис создается автоматически при деплое.

### Health Check
```bash
# Проверка здоровья приложения
docker-compose -f docker-compose.vps.yml exec roblox-garden python -c "print('✅ App is healthy')"

# Мониторинг ресурсов
docker stats roblox-garden-prod
```

### Автоматический мониторинг
Создается скрипт `health_monitor.sh`, который проверяет состояние каждые 5 минут.

## 🆘 Устранение неполадок

### Проблемы с Docker
```bash
# Проверка установки Docker
docker --version
docker-compose --version

# Проверка прав
docker ps

# Если нет прав
sudo usermod -aG docker $USER
# Затем logout/login
```

### Проблемы с контейнером
```bash
# Подключение к контейнеру
docker-compose -f docker-compose.vps.yml exec roblox-garden bash

# Проверка логов с ошибками
docker-compose -f docker-compose.vps.yml logs | grep -i error

# Пересборка образа
docker-compose -f docker-compose.vps.yml build --no-cache
```

### Очистка системы
```bash
# Удаление неиспользуемых образов
docker system prune -a

# Очистка томов
docker volume prune
```

## 🔄 Обновление

### Из Git (если настроено)
```bash
cd roblox-garden
git pull origin main
docker-compose -f docker-compose.vps.yml up --build -d
```

### Ручное обновление
1. Создайте новый архив на локальной машине
2. Загрузите на VPS
3. Остановите старую версию: `docker-compose -f docker-compose.vps.yml down`
4. Распакуйте новую версию
5. Запустите: `./deploy-vps.sh`

## 📋 Требования к VPS

- **OS**: Ubuntu 20.04+ или Debian 11+
- **RAM**: Минимум 1GB (рекомендуется 2GB)
- **Диск**: Минимум 10GB свободного места
- **CPU**: 1 vCore (достаточно shared CPU)
- **Сеть**: Стабильное интернет-соединение

## 🔑 Работа с root пользователем

### Автоматическое создание пользователя
Если вы запускаете скрипты от root, они автоматически:
- Создают пользователя `docker-user` для безопасной работы с Docker
- Настраивают все права и разрешения
- Конфигурируют systemd сервисы

### Варианты запуска
```bash
# Вариант 1: Запуск от root с интерактивным паролем
sudo su
./vps-setup.sh
# Будет предложено ввести пароль для docker-user
reboot

# Вариант 2: Запуск от root с автоматическим паролем
sudo su
DOCKER_USER_PASSWORD="your_secure_password" ./vps-setup.sh
reboot

# После перезагрузки можно работать от docker-user
su - docker-user  # потребует пароль
cd /home/docker-user/roblox-garden
./deploy-vps.sh

# Вариант 3: Запуск от обычного пользователя
./vps-setup.sh
sudo reboot

# После перезагрузки
./deploy-vps.sh
```

### Управление от разных пользователей
- **root**: Полный контроль, автоматическое создание docker-user
- **docker-user**: Специальный пользователь для Docker операций
- **обычный пользователь**: Требует sudo для системных операций

## ✅ Готово!

После успешного деплоя ваш бот будет:
- ✅ Автоматически запускаться при перезагрузке VPS
- ✅ Мониториться системой здоровья
- ✅ Логировать все события
- ✅ Ограничен по ресурсам для стабильной работы
- ✅ Защищен от неавторизованного доступа

Для получения помощи изучите файл `VPS_DEPLOY.md` или логи приложения.
