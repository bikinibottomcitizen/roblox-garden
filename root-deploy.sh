#!/bin/bash

# 🚀 Roblox Garden Bot - Simple Root Deploy
# Запускайте ТОЛЬКО от root на чистом VPS

set -e

if [[ $EUID -ne 0 ]]; then
   echo "❌ Запускайте только от root: sudo su -"
   exit 1
fi

echo "🏭 Roblox Garden Bot - Root Deploy"
echo "================================"

# Обновление системы
echo "📋 Обновление системы..."
apt update && apt upgrade -y

# Установка Docker
echo "📋 Установка Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Установка Docker Compose
echo "📋 Установка Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Создание директорий
echo "📋 Настройка директорий..."
mkdir -p logs secrets
chmod 755 logs
chmod 700 secrets

# Настройка секретов
echo "📋 Настройка секретов..."
read -p "Telegram Bot Token: " BOT_TOKEN
read -p "Updates Channel ID: " UPDATES_CHANNEL
read -p "Full Report Channel ID: " FULL_CHANNEL

echo "$BOT_TOKEN" > secrets/telegram_bot_token.txt
echo "$UPDATES_CHANNEL" > secrets/updates_channel_id.txt
echo "$FULL_CHANNEL" > secrets/full_channel_id.txt
chmod 600 secrets/*.txt

# Запуск приложения
echo "📋 Запуск приложения..."
docker-compose -f docker-compose.prod.yml up --build -d

# Создание systemd сервиса для автозапуска
echo "📋 Настройка автозапуска..."
cat > /etc/systemd/system/roblox-garden.service << EOF
[Unit]
Description=Roblox Garden Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$(pwd)
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable roblox-garden.service

echo "✅ Деплой завершен!"
echo "📋 Статус: docker-compose -f docker-compose.prod.yml ps"
echo "📋 Логи: docker-compose -f docker-compose.prod.yml logs -f"
echo "📋 Остановка: docker-compose -f docker-compose.prod.yml down"
