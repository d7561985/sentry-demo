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

# No need to generate environment files here - Docker will do it
echo "📝 Version $CURRENT_VERSION will be used for Docker build..."

# Export version for docker-compose
export APP_VERSION=$CURRENT_VERSION

# Enable Docker BuildKit for better caching
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Start services in production mode
echo "🔄 Starting Docker containers..."
echo "📦 Building with version: $APP_VERSION"
echo "🚀 Using Docker BuildKit for efficient caching"

# Stop existing containers
docker-compose down

# Build with caching (remove --no-cache for faster builds)
echo "🔨 Building services (using cache when possible)..."
docker-compose build

# Force rebuild only if explicitly requested
if [ "$1" = "--force-rebuild" ]; then
    echo "⚠️  Force rebuild requested, ignoring cache..."
    docker-compose build --no-cache
fi

docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "✅ Services are running in production mode!"
echo ""

# Upload source maps from the running container if token is available
if [ -n "$SENTRY_AUTH_TOKEN" ]; then
    echo "📤 Uploading source maps from deployed container..."
    ./services/frontend/upload-sourcemaps-from-docker.sh
    echo ""
fi

echo "📊 Access points:"
echo "  - Frontend: http://localhost:4200"
echo "  - API Gateway: http://localhost:8080"
echo ""
echo "🔍 View logs:"
echo "  docker-compose logs -f frontend"
echo ""
echo "🛑 To stop:"
echo "  docker-compose down"
echo ""
echo "💡 Tips:"
echo "  - Builds use Docker cache for faster subsequent runs"
echo "  - Force rebuild: ./start-prod.sh --force-rebuild"