#!/bin/bash

# 🐧 Roblox Garden Bot - Автоматическая установка для Linux
# Создает виртуальное окружение, устанавливает зависимости, настраивает каналы и запускает бота

set -e

echo "🐧 Roblox Garden Bot - Установка для Linux"
echo "============================================"

# Определение дистрибутива
if command -v lsb_release &> /dev/null; then
    DISTRO=$(lsb_release -si)
    VERSION=$(lsb_release -sr)
elif [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$NAME
    VERSION=$VERSION_ID
else
    DISTRO="Unknown"
    VERSION="Unknown"
fi

echo "🖥️ Обнаружена система: $DISTRO $VERSION"

# Функция для вывода статуса
print_status() {
    echo
    echo "📋 $1"
    echo "----------------------------------------"
}

# Проверка и установка Python
print_status "Проверка Python"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Устанавливаем..."
    
    # Определяем менеджер пакетов и устанавливаем Python
    if command -v apt &> /dev/null; then
        # Debian/Ubuntu
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL 7
        sudo yum install -y python3 python3-pip python3-venv
    elif command -v dnf &> /dev/null; then
        # Fedora/CentOS 8+/RHEL 8+
        sudo dnf install -y python3 python3-pip python3-venv
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        sudo pacman -S --noconfirm python python-pip
    elif command -v zypper &> /dev/null; then
        # openSUSE
        sudo zypper install -y python3 python3-pip python3-venv
    elif command -v apk &> /dev/null; then
        # Alpine Linux
        sudo apk add python3 python3-dev py3-pip py3-virtualenv
    else
        echo "❌ Неизвестный менеджер пакетов. Установите Python 3.8+ вручную."
        exit 1
    fi
else
    echo "✅ Python уже установлен"
fi

# Проверка версии Python
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Найден Python $PYTHON_VERSION"

# Проверка минимальной версии
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "✅ Версия Python подходит (требуется 3.8+)"
else
    echo "❌ Требуется Python 3.8 или выше. Текущая версия: $PYTHON_VERSION"
    exit 1
fi

# Проверка и установка дополнительных пакетов
print_status "Проверка системных зависимостей"

# Проверяем curl для загрузки файлов
if ! command -v curl &> /dev/null; then
    echo "📥 Устанавливаем curl..."
    if command -v apt &> /dev/null; then
        sudo apt install -y curl
    elif command -v yum &> /dev/null; then
        sudo yum install -y curl
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y curl
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm curl
    elif command -v zypper &> /dev/null; then
        sudo zypper install -y curl
    elif command -v apk &> /dev/null; then
        sudo apk add curl
    fi
fi

# Проверяем git
if ! command -v git &> /dev/null; then
    echo "📥 Устанавливаем git..."
    if command -v apt &> /dev/null; then
        sudo apt install -y git
    elif command -v yum &> /dev/null; then
        sudo yum install -y git
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y git
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm git
    elif command -v zypper &> /dev/null; then
        sudo zypper install -y git
    elif command -v apk &> /dev/null; then
        sudo apk add git
    fi
fi

echo "✅ Системные зависимости готовы"

# 1. Создание виртуального окружения
print_status "Создание виртуального окружения"
if [[ ! -d ".venv" ]]; then
    python3 -m venv .venv
    echo "✅ Виртуальное окружение создано"
else
    echo "✅ Виртуальное окружение уже существует"
fi

# Активация виртуального окружения
source .venv/bin/activate
echo "✅ Виртуальное окружение активировано"

# 2. Обновление pip и установка зависимостей
print_status "Установка зависимостей"
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Зависимости установлены"

# 3. Создание директории для логов
print_status "Подготовка окружения"
mkdir -p logs
mkdir -p secrets
echo "✅ Директории созданы"

# 4. Проверка файла .env
print_status "Проверка конфигурации"
if [[ ! -f ".env" ]]; then
    echo "❌ Файл .env не найден! Создаем новый..."
    cp .env.example .env
    echo "✅ Файл .env создан из шаблона"
fi

# Проверка токена бота
if ! grep -q "TELEGRAM_BOT_TOKEN=" .env || grep -q "your_bot_token_here" .env; then
    echo "⚠️  Не настроен токен Telegram бота"
    echo ""
    echo "🤖 Настройка Telegram бота"
    echo "════════════════════════════"
    echo ""
    echo "1. Перейдите к @BotFather в Telegram"
    echo "2. Отправьте команду /newbot"
    echo "3. Следуйте инструкциям для создания бота"
    echo "4. Скопируйте токен из сообщения BotFather"
    echo ""
    echo "Токен выглядит примерно так: 1234567890:ABCdefGhIjKlMnOpQrStUvWxYz"
    echo ""
    
    # Запрос токена
    while true; do
        read -p "🔑 Введите токен вашего бота: " bot_token
        
        if [[ -z "$bot_token" ]]; then
            echo "❌ Токен не может быть пустым!"
            continue
        fi
        
        if [[ ! "$bot_token" =~ ^[0-9]+:.+ ]]; then
            echo "❌ Неверный формат токена! Должен быть вида: 1234567890:ABC..."
            continue
        fi
        
        break
    done
    
    # Обновление токена в .env
    if grep -q "TELEGRAM_BOT_TOKEN=" .env; then
        sed -i.bak "s/TELEGRAM_BOT_TOKEN=.*/TELEGRAM_BOT_TOKEN=$bot_token/" .env
    else
        echo "TELEGRAM_BOT_TOKEN=$bot_token" >> .env
    fi
    
    echo "✅ Токен сохранен в .env"
    echo ""
    echo "🔧 Запускаем мастер настройки каналов..."
    echo ""
    
    # Запуск настройки каналов
    python3 get_channel_ids.py
    
    echo ""
    echo "✅ Настройка каналов завершена"
else
    echo "✅ Конфигурация найдена"
fi

# 5. Проверка настроек каналов
if grep -q "your_.*_channel_id" .env 2>/dev/null; then
    echo "⚠️  Обнаружены незаполненные ID каналов"
    echo ""
    echo "🔧 Запускаем мастер настройки каналов..."
    echo ""
    
    # Запуск настройки каналов
    python3 get_channel_ids.py
    
    echo ""
    echo "✅ Настройка каналов завершена"
fi

# 6. Создание systemd сервиса (опционально)
print_status "Настройка автозапуска"
echo "Хотите настроить автозапуск бота при старте системы? (y/N)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    SERVICE_NAME="roblox-garden-bot"
    SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
    WORK_DIR="$(pwd)"
    USER="$(whoami)"
    
    echo "🔧 Создание systemd сервиса..."
    
    # Проверяем наличие systemd
    if ! command -v systemctl &> /dev/null; then
        echo "❌ systemd не найден. Пропускаем создание сервиса."
    else
        sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Roblox Garden Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORK_DIR
Environment=PATH=$WORK_DIR/.venv/bin
ExecStart=$WORK_DIR/.venv/bin/python -m roblox_garden
Restart=always
RestartSec=10
StandardOutput=append:$WORK_DIR/logs/systemd.log
StandardError=append:$WORK_DIR/logs/systemd-error.log

[Install]
WantedBy=multi-user.target
EOF

        sudo systemctl daemon-reload
        sudo systemctl enable "$SERVICE_NAME"
        
        echo "✅ Systemd сервис создан и включен"
        echo ""
        echo "Управление сервисом:"
        echo "  sudo systemctl start $SERVICE_NAME      # Запуск"
        echo "  sudo systemctl stop $SERVICE_NAME       # Остановка"
        echo "  sudo systemctl restart $SERVICE_NAME    # Перезапуск"
        echo "  sudo systemctl status $SERVICE_NAME     # Статус"
        echo "  journalctl -u $SERVICE_NAME -f          # Логи"
        echo "  tail -f logs/systemd.log                # Логи приложения"
    fi
else
    echo "⏭️ Пропускаем настройку автозапуска"
fi

# 7. Создание полезных скриптов
print_status "Создание вспомогательных скриптов"

# Скрипт запуска
cat > start.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
python -m roblox_garden
EOF
chmod +x start.sh

# Скрипт запуска в фоне
cat > start_background.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
nohup python -m roblox_garden > logs/bot.log 2>&1 &
echo $! > bot.pid
echo "🚀 Бот запущен в фоне (PID: $(cat bot.pid))"
echo "📋 Логи: tail -f logs/bot.log"
echo "⛔ Остановка: kill $(cat bot.pid)"
EOF
chmod +x start_background.sh

# Скрипт остановки
cat > stop.sh << 'EOF'
#!/bin/bash
if [[ -f "bot.pid" ]]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "⛔ Бот остановлен (PID: $PID)"
        rm bot.pid
    else
        echo "⚠️  Процесс с PID $PID не найден"
        rm bot.pid
    fi
else
    echo "⚠️  Файл bot.pid не найден"
fi
EOF
chmod +x stop.sh

# Скрипт просмотра логов
cat > logs.sh << 'EOF'
#!/bin/bash
if [[ -f "logs/bot.log" ]]; then
    tail -f logs/bot.log
elif [[ -f "logs/systemd.log" ]]; then
    tail -f logs/systemd.log
else
    echo "❌ Файлы логов не найдены. Запустите бота сначала."
fi
EOF
chmod +x logs.sh

# Скрипт обновления
cat > update.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🔄 Обновление из git..."
git pull

echo "🔄 Обновление зависимостей..."
source .venv/bin/activate
pip install --upgrade -r requirements.txt
echo "✅ Обновление завершено"

# Перезапуск сервиса если он включен
if systemctl is-enabled roblox-garden-bot &> /dev/null; then
    echo "🔄 Перезапускаем systemd сервис..."
    sudo systemctl restart roblox-garden-bot
    echo "✅ Сервис перезапущен"
fi
EOF
chmod +x update.sh

# Скрипт статуса
cat > status.sh << 'EOF'
#!/bin/bash
echo "📊 СТАТУС ROBLOX GARDEN BOT"
echo "============================"

# Проверяем systemd сервис
if systemctl is-enabled roblox-garden-bot &> /dev/null; then
    echo "🔧 Systemd сервис: $(systemctl is-active roblox-garden-bot)"
    echo "   Автозапуск: $(systemctl is-enabled roblox-garden-bot)"
    echo "   Статус: $(systemctl status roblox-garden-bot --no-pager -l)"
elif [[ -f "bot.pid" ]]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null; then
        echo "🟢 Фоновый процесс: Запущен (PID: $PID)"
    else
        echo "🔴 Фоновый процесс: Не найден (PID: $PID)"
    fi
else
    echo "🔴 Бот не запущен"
fi

# Показываем последние логи
echo ""
echo "📋 Последние логи:"
echo "-------------------"
if [[ -f "logs/systemd.log" ]]; then
    tail -10 logs/systemd.log
elif [[ -f "logs/bot.log" ]]; then
    tail -10 logs/bot.log
else
    echo "Логи не найдены"
fi
EOF
chmod +x status.sh

echo "✅ Вспомогательные скрипты созданы:"
echo "  ./start.sh           # Запуск в терминале"
echo "  ./start_background.sh # Запуск в фоне"
echo "  ./stop.sh            # Остановка фонового процесса"
echo "  ./logs.sh            # Просмотр логов"
echo "  ./update.sh          # Обновление и перезапуск"
echo "  ./status.sh          # Статус бота"

# 8. Настройка firewall (если нужно)
print_status "Проверка сетевых настроек"
echo "Бот использует исходящие HTTPS соединения (443) для:"
echo "  • Telegram API"
echo "  • Roblox Garden API"
echo ""
echo "Входящие порты НЕ требуются."
echo "✅ Настройка сети не требуется"

# 9. Финальная проверка и запуск
print_status "Установка завершена!"
echo "✅ Виртуальное окружение создано"
echo "✅ Зависимости установлены"
echo "✅ Конфигурация проверена"
echo "✅ Вспомогательные скрипты созданы"

# Показываем информацию о системе
echo ""
echo "🖥️ Информация о системе:"
echo "   ОС: $DISTRO $VERSION"
echo "   Python: $PYTHON_VERSION"
echo "   Пользователь: $(whoami)"
echo "   Директория: $(pwd)"

echo ""
echo "🚀 Готово к запуску!"
echo ""
echo "Выберите способ запуска:"
echo "1. В терминале (с выводом логов)"
echo "2. В фоновом режиме"
echo "3. Как systemd сервис (если настроен)"
echo "4. Выйти (запустить позже вручную)"
echo ""
read -p "Ваш выбор (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Запускаем бота в терминале..."
        echo "Для остановки нажмите Ctrl+C"
        echo ""
        sleep 2
        python -m roblox_garden
        ;;
    2)
        echo ""
        echo "🚀 Запускаем бота в фоновом режиме..."
        ./start_background.sh
        echo ""
        echo "Для просмотра логов: ./logs.sh"
        echo "Для остановки: ./stop.sh"
        echo "Для статуса: ./status.sh"
        ;;
    3)
        if systemctl is-enabled roblox-garden-bot &> /dev/null; then
            echo ""
            echo "🚀 Запускаем systemd сервис..."
            sudo systemctl start roblox-garden-bot
            echo "✅ Сервис запущен"
            echo ""
            echo "Для просмотра статуса: sudo systemctl status roblox-garden-bot"
            echo "Для просмотра логов: journalctl -u roblox-garden-bot -f"
        else
            echo "❌ Systemd сервис не настроен"
        fi
        ;;
    4)
        echo ""
        echo "✅ Установка завершена."
        echo ""
        echo "Для запуска используйте:"
        echo "  ./start.sh           # В терминале"
        echo "  ./start_background.sh # В фоне"
        echo "  ./status.sh          # Проверить статус"
        ;;
    *)
        echo "Неверный выбор. Выход."
        ;;
esac

echo ""
echo "📖 Полезные команды:"
echo "  ./status.sh          # Проверить статус"
echo "  ./logs.sh            # Посмотреть логи"
echo "  ./update.sh          # Обновить бота"
echo "  ./stop.sh            # Остановить"
echo ""
echo "🎉 Установка завершена успешно!"
