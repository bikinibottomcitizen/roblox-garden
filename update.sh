#!/bin/bash
cd "$(dirname "$0")"
echo "🔄 Обновление зависимостей..."
source .venv/bin/activate
pip install --upgrade -r requirements.txt
echo "✅ Обновление завершено"
