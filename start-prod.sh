#!/bin/bash

# Production start script with source map upload using debug-ids

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

echo "🚀 Starting Sentry POC in PRODUCTION mode..."
echo "📝 Version: $CURRENT_VERSION"
echo "📝 This mode includes:"
echo "  - Optimized production build"
echo "  - Source maps with debug-ids"
echo "  - Automatic source map upload to Sentry"
echo "  - Production environment settings"
echo ""

# Check for Sentry auth token
if [ -z "$SENTRY_AUTH_TOKEN" ]; then
    echo "⚠️  Warning: SENTRY_AUTH_TOKEN not set"
    echo "   Source maps will not be uploaded to Sentry"
    echo "   Set it in .env file to enable source map upload"
    echo ""
fi

# Generate environment files with new version
echo "📝 Generating environment files with version $CURRENT_VERSION..."
cd services/frontend
APP_VERSION=$CURRENT_VERSION node scripts/generate-env.js

# Check if frontend has its own .env file
if [ -f .env ]; then
    echo "📋 Loading frontend-specific environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Build and upload source maps if token is available
if [ -n "$SENTRY_AUTH_TOKEN" ]; then
    echo "🔨 Building production version with source map upload..."
    echo "   Using SENTRY_ORG: ${SENTRY_ORG:-not set}"
    echo "   Using SENTRY_PROJECT: ${SENTRY_PROJECT:-not set}"
    echo "   Using APP_VERSION: $CURRENT_VERSION"
    echo "   Sentry CLI version: $(npx @sentry/cli --version 2>/dev/null || echo 'not installed')"
    export APP_VERSION=$CURRENT_VERSION
    npm run build:upload
else
    echo "🔨 Building production version without source map upload..."
    npm run build:dev
fi

cd ../..

# Export version for docker-compose
export APP_VERSION=$CURRENT_VERSION

# Start services in production mode
echo "🔄 Starting Docker containers..."
docker-compose up -d --build frontend

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "✅ Services are running in production mode!"
echo ""
echo "📊 Access points:"
echo "  - Frontend: http://localhost:4200"
echo "  - API Gateway: http://localhost:8080"
echo ""
echo "🔍 View logs:"
echo "  docker-compose logs -f frontend"
echo ""
echo "🛑 To stop:"
echo "  docker-compose down"