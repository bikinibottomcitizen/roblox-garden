#!/bin/bash

# Deployment script for Roblox Garden Bot
# This script builds and deploys the Docker container

set -e  # Exit on error

echo "🚀 Roblox Garden Bot - Docker Deployment"
echo "========================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please copy .env.example to .env and configure your settings:"
    echo "   cp .env.example .env"
    echo "   # Edit .env with your Telegram bot token and channel IDs"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose not found!"
    echo "Please install docker-compose and try again."
    exit 1
fi

# Load environment variables to check required settings
source .env

# Validate required environment variables
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "your_bot_token_here" ]; then
    echo "❌ Error: TELEGRAM_BOT_TOKEN not configured in .env"
    exit 1
fi

if [ -z "$UPDATES_CHANNEL_ID" ] || [ "$UPDATES_CHANNEL_ID" = "your_updates_channel_id_here" ]; then
    echo "❌ Error: UPDATES_CHANNEL_ID not configured in .env"
    exit 1
fi

if [ -z "$FULL_CHANNEL_ID" ] || [ "$FULL_CHANNEL_ID" = "your_full_channel_id_here" ]; then
    echo "❌ Error: FULL_CHANNEL_ID not configured in .env"
    exit 1
fi

echo "✅ Configuration validated"

# Create logs directory if it doesn't exist
mkdir -p logs

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans || true

# Build and start the application
echo "🔨 Building Docker image..."
docker-compose build --no-cache

echo "🚀 Starting Roblox Garden Bot..."
docker-compose up -d

# Show status
echo "📊 Container status:"
docker-compose ps

# Show logs
echo ""
echo "📋 Recent logs (press Ctrl+C to stop):"
echo "----------------------------------------"
docker-compose logs -f --tail=20

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📱 Useful commands:"
echo "  docker-compose logs -f           # View live logs"
echo "  docker-compose restart           # Restart bot"
echo "  docker-compose down              # Stop bot"
echo "  docker-compose up -d             # Start bot in background"
