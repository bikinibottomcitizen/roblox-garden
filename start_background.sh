#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
nohup python -m roblox_garden > logs/bot.log 2>&1 &
echo $! > bot.pid
echo "🚀 Бот запущен в фоне (PID: $(cat bot.pid))"
echo "📋 Логи: tail -f logs/bot.log"
echo "⛔ Остановка: kill $(cat bot.pid)"
