#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your Sentry DSNs"
    exit 1
fi

# Check if Sentry DSNs are configured
if grep -q "YOUR_KEY" .env; then
    echo "❌ Please configure Sentry DSNs in .env file"
    echo "   Replace YOUR_KEY placeholders with actual Sentry DSNs"
    exit 1
fi

echo "🚀 Starting Sentry POC services..."

# Start services
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

services=("frontend:4200" "api-gateway:8080" "user-service:8081" "game-engine:8082" "payment-service:8083")

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health | grep -q "200"; then
        echo "✅ $name is healthy"
    else
        echo "❌ $name is not responding"
    fi
done

echo ""
echo "🎮 Frontend available at: http://localhost:4200"
echo "📊 Check your Sentry dashboard for traces!"
echo ""
echo "🛑 To stop: docker-compose down"