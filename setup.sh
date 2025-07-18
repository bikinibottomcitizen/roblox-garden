#!/bin/bash

# 🚀 Roblox Garden Bot - Автоматическая установка и запуск
# Создает виртуальное окружение, устанавливает зависимости, настраивает каналы и запускает бота

set -e

echo "🌱 Roblox Garden Bot - Автоматическая установка"
echo "=============================================="

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.8+ и попробуйте снова."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Найден Python $PYTHON_VERSION"

# Функция для вывода статуса
print_status() {
    echo
    echo "📋 $1"
    echo "----------------------------------------"
}

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

# 6. Тестирование подключения
print_status "Тестирование подключения"
echo "🔍 Проверяем подключение к Telegram..."

if python3 test_telegram.py; then
    echo "✅ Подключение к Telegram успешно"
else
    echo "❌ Ошибка подключения к Telegram"
    echo "Проверьте настройки в .env файле"
    exit 1
fi

# 7. Создание системного сервиса (опционально)
print_status "Настройка автозапуска"
echo "Хотите настроить автозапуск бота при старте системы? (y/N)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    SERVICE_NAME="roblox-garden-bot"
    SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
    WORK_DIR="$(pwd)"
    
    echo "🔧 Создание systemd сервиса..."
    
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
fi

# 8. Создание полезных скриптов
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
else
    echo "❌ Файл логов не найден. Запустите бота сначала."
fi
EOF
chmod +x logs.sh

# Скрипт обновления
cat > update.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🔄 Обновление зависимостей..."
source .venv/bin/activate
pip install --upgrade -r requirements.txt
echo "✅ Обновление завершено"
EOF
chmod +x update.sh

echo "✅ Вспомогательные скрипты созданы:"
echo "  ./start.sh           # Запуск в терминале"
echo "  ./start_background.sh # Запуск в фоне"
echo "  ./stop.sh            # Остановка фонового процесса"
echo "  ./logs.sh            # Просмотр логов"
echo "  ./update.sh          # Обновление зависимостей"

# 9. Финальная проверка и запуск
print_status "Установка завершена!"
echo "✅ Виртуальное окружение создано"
echo "✅ Зависимости установлены"
echo "✅ Конфигурация проверена"
echo "✅ Telegram подключение протестировано"
echo "✅ Вспомогательные скрипты созданы"

echo ""
echo "🚀 Готово к запуску!"
echo ""
echo "Выберите способ запуска:"
echo "1. В терминале (с выводом логов)"
echo "2. В фоновом режиме"
echo "3. Выйти (запустить позже вручную)"
echo ""
read -p "Ваш выбор (1-3): " choice

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
        ;;
    3)
        echo ""
        echo "✅ Установка завершена."
        echo ""
        echo "Для запуска используйте:"
        echo "  ./start.sh           # В терминале"
        echo "  ./start_background.sh # В фоне"
        ;;
    *)
        echo "Неверный выбор. Выход."
        ;;
esac
