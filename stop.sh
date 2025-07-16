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
