#!/bin/bash

# Fast production start with intelligent caching
# Only rebuilds services that have changed

# Load environment variables from .env file
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  Warning: .env file not found"
    echo "   Copy .env.example to .env and configure your settings"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(cat .version)

echo "🚀 Starting Sentry POC in FAST PRODUCTION mode..."
echo "📝 Version: $CURRENT_VERSION"
echo "⚡ Using smart caching - only rebuilding changed services"
echo ""

# Export version for docker-compose
export APP_VERSION=$CURRENT_VERSION

# Enable Docker BuildKit for maximum performance
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export BUILDKIT_PROGRESS=plain

# Check which services need rebuilding
echo "🔍 Checking for changes..."

# Build only changed services
echo "🔨 Building changed services..."
docker-compose build --parallel

# Restart only changed services
echo "🔄 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

echo ""
echo "✅ Services are running in production mode!"
echo ""

# Upload source maps if frontend was rebuilt
FRONTEND_CHANGED=$(docker-compose ps -q frontend 2>/dev/null)
if [ -n "$FRONTEND_CHANGED" ] && [ -n "$SENTRY_AUTH_TOKEN" ]; then
    echo "📤 Frontend was updated, uploading source maps..."
    ./services/frontend/upload-sourcemaps-from-docker.sh
    echo ""
fi

echo "📊 Access points:"
echo "  - Frontend: http://localhost:4200"
echo "  - API Gateway: http://localhost:8080"
echo ""
echo "💡 This script uses smart caching:"
echo "  - Only rebuilds changed services"
echo "  - Uses Docker BuildKit for faster builds"
echo "  - Parallel builds when possible"
echo ""
echo "🔍 Check specific service logs:"
echo "  docker-compose logs -f [service-name]"