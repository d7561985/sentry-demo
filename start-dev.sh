#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  Warning: .env file not found"
    echo "   Copy .env.example to .env and configure your settings"
    exit 1
fi

# Increment version
source ./scripts/increment-version.sh
CURRENT_VERSION=$(cat .version)

echo "🚀 Starting Sentry POC in DEVELOPMENT mode..."
echo "📝 Version: $CURRENT_VERSION"
echo "📝 This mode includes:"
echo "  - Source maps with full debugging (with debug-ids)"
echo "  - Hot reload for frontend"
echo "  - Debug logging enabled"
echo "  - Development environment settings"
echo "  - No source map upload to Sentry (dev mode)"
echo ""

# Generate environment files with new version
echo "📝 Generating environment files with version $CURRENT_VERSION..."
cd services/frontend
APP_VERSION=$CURRENT_VERSION node scripts/generate-env.js
cd ../..

# Export version for docker-compose
export APP_VERSION=$CURRENT_VERSION

# Start services with dev overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "✅ Services are starting!"
echo ""
echo "📊 Access points:"
echo "  - Frontend (dev): http://localhost:4200"
echo "  - API Gateway: http://localhost:8080"
echo ""
echo "🔍 View logs:"
echo "  docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f frontend"
echo ""
echo "🛑 To stop:"
echo "  docker-compose -f docker-compose.yml -f docker-compose.dev.yml down"