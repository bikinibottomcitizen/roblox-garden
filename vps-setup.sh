# Как было раньше
./vps-setup.sh
sudo reboot
./deploy-vps.sh#!/bin/bash

# 🚀 Быстрый деплой Roblox Garden Bot на VPS
# Запускайте этот скрипт на чистом VPS с Ubuntu/Debian

set -e

echo "🏭 Roblox Garden Bot - VPS Quick Deploy"
echo "======================================"

# Определение пользователя и настройка переменных
if [[ $EUID -eq 0 ]]; then
    echo "⚠️  Запуск от имени root"
    # Создание пользователя для Docker, если его нет
    if ! id "docker-user" &>/dev/null; then
        echo "📋 Создание пользователя docker-user..."
        useradd -m -s /bin/bash docker-user
        usermod -aG sudo docker-user
        
        # Установка пароля для docker-user
        echo "🔐 Установка пароля для пользователя docker-user"
        
        # Проверяем, задан ли пароль через переменную окружения
        if [[ -n "${DOCKER_USER_PASSWORD}" ]]; then
            echo "docker-user:${DOCKER_USER_PASSWORD}" | chpasswd
            echo "✅ Пароль установлен из переменной окружения"
        else
            echo "Введите пароль для пользователя docker-user:"
            passwd docker-user
            echo "✅ Пароль установлен интерактивно"
        fi
        
        echo "✅ Пользователь docker-user создан с паролем"
    else
        echo "✅ Пользователь docker-user уже существует"
    fi
    DOCKER_USER="docker-user"
    USER_HOME="/home/docker-user"
    SUDO_CMD=""
else
    echo "📋 Запуск от имени пользователя: $USER"
    DOCKER_USER="$USER"
    USER_HOME="$HOME"
    SUDO_CMD="sudo"
fi

# Функция для вывода статуса
print_status() {
    echo
    echo "📋 $1"
    echo "----------------------------------------"
}

# 1. Обновление системы
print_status "Обновление системы"
$SUDO_CMD apt update && $SUDO_CMD apt upgrade -y

# 2. Установка Docker
print_status "Установка Docker"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    $SUDO_CMD sh get-docker.sh
    $SUDO_CMD usermod -aG docker $DOCKER_USER
    rm get-docker.sh
    echo "✅ Docker установлен"
else
    echo "✅ Docker уже установлен"
    # Убеждаемся, что пользователь в группе docker
    $SUDO_CMD usermod -aG docker $DOCKER_USER
fi

# 3. Установка Docker Compose
print_status "Установка Docker Compose"
if ! command -v docker-compose &> /dev/null; then
    $SUDO_CMD curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    $SUDO_CMD chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose установлен"
else
    echo "✅ Docker Compose уже установлен"
fi

# 4. Создание рабочей директории
print_status "Настройка рабочей директории"
$SUDO_CMD mkdir -p $USER_HOME/roblox-garden
if [[ $EUID -eq 0 ]]; then
    $SUDO_CMD chown -R $DOCKER_USER:$DOCKER_USER $USER_HOME/roblox-garden
fi
cd $USER_HOME/roblox-garden

# 5. Скачивание файлов проекта (если нет git)
print_status "Получение файлов проекта"
if [[ ! -f "docker-compose.prod.yml" && ! -f "docker-compose.vps.yml" ]]; then
    echo "📁 Создайте файлы проекта в $USER_HOME/roblox-garden/"
    echo "Или склонируйте репозиторий:"
    echo "git clone <your-repo-url> $USER_HOME/roblox-garden"
    echo
    echo "Необходимые файлы:"
    echo "- docker-compose.vps.yml (или docker-compose.prod.yml)"
    echo "- Dockerfile"
    echo "- requirements.txt"
    echo "- roblox_garden/ (папка с кодом)"
    echo
    echo "После добавления файлов запустите: ./deploy-vps.sh"
    exit 1
fi

# 6. Создание systemd сервиса
print_status "Настройка автозапуска"
COMPOSE_FILE="docker-compose.vps.yml"
if [[ ! -f "$COMPOSE_FILE" ]]; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

$SUDO_CMD tee /etc/systemd/system/roblox-garden.service > /dev/null <<EOF
[Unit]
Description=Roblox Garden Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$USER_HOME/roblox-garden
ExecStart=/usr/local/bin/docker-compose -f $COMPOSE_FILE up -d
ExecStop=/usr/local/bin/docker-compose -f $COMPOSE_FILE down
TimeoutStartSec=0
User=$DOCKER_USER
Group=$DOCKER_USER

[Install]
WantedBy=multi-user.target
EOF

$SUDO_CMD systemctl daemon-reload
$SUDO_CMD systemctl enable roblox-garden.service

# 7. Настройка мониторинга
print_status "Настройка мониторинга"
cat > health_monitor.sh << EOF
#!/bin/bash
cd $USER_HOME/roblox-garden

COMPOSE_FILE="docker-compose.vps.yml"
if [[ ! -f "\$COMPOSE_FILE" ]]; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

if ! docker-compose -f \$COMPOSE_FILE ps | grep -q "Up"; then
    echo "\$(date): Service is down, restarting..." >> logs/health.log
    docker-compose -f \$COMPOSE_FILE up -d
fi
EOF

chmod +x health_monitor.sh
if [[ $EUID -eq 0 ]]; then
    chown $DOCKER_USER:$DOCKER_USER health_monitor.sh
fi

# Добавление в cron для нужного пользователя
if [[ $EUID -eq 0 ]]; then
    # Создаем cron job для docker-user
    echo "*/5 * * * * $USER_HOME/roblox-garden/health_monitor.sh" | $SUDO_CMD crontab -u $DOCKER_USER -
else
    # Добавляем в cron текущего пользователя
    (crontab -l 2>/dev/null | grep -v "health_monitor.sh"; echo "*/5 * * * * $USER_HOME/roblox-garden/health_monitor.sh") | crontab -
fi

# 8. Создание полезных алиасов
print_status "Создание алиасов"

# Определяем правильный файл конфигурации Docker Compose
COMPOSE_FILE="docker-compose.vps.yml"
if [[ ! -f "$COMPOSE_FILE" ]]; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

# Добавляем алиасы в bashrc нужного пользователя
if [[ $EUID -eq 0 ]]; then
    BASHRC_FILE="$USER_HOME/.bashrc"
else
    BASHRC_FILE="$HOME/.bashrc"
fi

cat >> $BASHRC_FILE << EOF

# Roblox Garden Bot aliases
alias rg-logs='docker-compose -f $USER_HOME/roblox-garden/$COMPOSE_FILE logs -f'
alias rg-status='docker-compose -f $USER_HOME/roblox-garden/$COMPOSE_FILE ps'
alias rg-restart='cd $USER_HOME/roblox-garden && docker-compose -f $COMPOSE_FILE restart'
alias rg-stop='cd $USER_HOME/roblox-garden && docker-compose -f $COMPOSE_FILE down'
alias rg-start='cd $USER_HOME/roblox-garden && docker-compose -f $COMPOSE_FILE up -d'
alias rg-update='cd $USER_HOME/roblox-garden && git pull && docker-compose -f $COMPOSE_FILE up --build -d'
EOF

if [[ $EUID -eq 0 ]]; then
    chown $DOCKER_USER:$DOCKER_USER $BASHRC_FILE
fi

print_status "Установка завершена!"
echo "✅ Docker установлен и настроен"
echo "✅ Systemd сервис создан"
echo "✅ Мониторинг настроен"
echo "✅ Алиасы добавлены"
echo
if [[ $EUID -eq 0 ]]; then
    echo "🔄 Необходимо перелогиниться как пользователь $DOCKER_USER для применения прав Docker"
    echo "su - $DOCKER_USER"
    echo
    echo "📋 Или перезагрузите систему:"
    echo "reboot"
    echo
    echo "📋 После перелогина/перезагрузки:"
    echo "1. cd $USER_HOME/roblox-garden"
    echo "2. ./deploy-vps.sh (или ./deploy-prod.sh)"
else
    echo "🔄 Требуется перезагрузка для применения прав Docker:"
    echo "sudo reboot"
    echo
    echo "📋 После перезагрузки:"
    echo "1. cd $USER_HOME/roblox-garden"
    echo "2. ./deploy-vps.sh (или ./deploy-prod.sh)"
fi
echo
echo "🔧 Полезные команды:"
echo "- rg-logs     # Просмотр логов"
echo "- rg-status   # Статус сервиса"
echo "- rg-restart  # Перезапуск"
echo "- rg-stop     # Остановка"
echo "- rg-start    # Запуск"
echo "- rg-update   # Обновление из git"
