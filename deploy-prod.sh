#!/bin/bash

# Production deployment script with secrets management
# This script sets up secure production deployment

set -e

echo "🏭 Roblox Garden Bot - Production Deployment"
echo "============================================"

# Check if running as root (recommended for production)
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Warning: Running as non-root user"
    echo "For production, consider running as root or with proper permissions"
fi

# Create secrets directory
mkdir -p secrets
chmod 700 secrets

# Function to create secret file
create_secret() {
    local secret_name=$1
    local secret_file="secrets/${secret_name}.txt"
    
    if [ ! -f "$secret_file" ]; then
        echo "📝 Creating secret: $secret_name"
        read -s -p "Enter $secret_name: " secret_value
        echo
        echo "$secret_value" > "$secret_file"
        chmod 600 "$secret_file"
        echo "✅ Secret $secret_name created"
    else
        echo "✅ Secret $secret_name already exists"
    fi
}

# Create required secrets
echo "🔐 Setting up secrets..."
create_secret "telegram_bot_token"
create_secret "updates_channel_id" 
create_secret "full_channel_id"

# Create logs directory
mkdir -p logs
chmod 755 logs

# Validate Docker setup
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    exit 1
fi

if ! docker-compose --version > /dev/null 2>&1; then
    echo "❌ Error: docker-compose not found!"
    exit 1
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down --remove-orphans || true

# Pull latest images
echo "📥 Pulling latest base images..."
docker pull python:3.11-slim

# Build production image
echo "🔨 Building production image..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Start production deployment
echo "🚀 Starting production deployment..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for health check
echo "⏳ Waiting for health check..."
sleep 30

# Check deployment status
echo "📊 Deployment status:"
docker-compose -f docker-compose.prod.yml ps

# Show resource usage
echo "💾 Resource usage:"
docker stats --no-stream

# Setup log rotation
echo "📝 Setting up log rotation..."
cat > /etc/logrotate.d/roblox-garden << 'EOF'
/path/to/roblox-garden/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    postrotate
        docker-compose -f /path/to/roblox-garden/docker-compose.prod.yml restart roblox-garden
    endscript
}
EOF

echo "✅ Production deployment complete!"
echo ""
echo "📱 Management commands:"
echo "  docker-compose -f docker-compose.prod.yml logs -f    # View logs"
echo "  docker-compose -f docker-compose.prod.yml restart    # Restart"
echo "  docker-compose -f docker-compose.prod.yml down       # Stop"
echo "  docker stats                                          # Monitor resources"
echo ""
echo "🔐 Security notes:"
echo "  - Secrets are stored in ./secrets/ with 600 permissions"
echo "  - Log rotation is configured for /etc/logrotate.d/"
echo "  - Container runs as non-root user"
echo "  - Resource limits are enforced"
