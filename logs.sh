#!/bin/bash
if [[ -f "logs/bot.log" ]]; then
    tail -f logs/bot.log
else
    echo "❌ Файл логов не найден. Запустите бота сначала."
fi
