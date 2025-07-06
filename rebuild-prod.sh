#!/bin/bash

echo "🔨 Rebuilding and starting in production mode..."

# Load environment variables
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Stop everything
echo "🛑 Stopping all containers..."
docker-compose down

# Remove old images
echo "🗑️  Removing old frontend image..."
docker rmi sentry-poc-frontend:latest 2>/dev/null || true

# Clean build cache
echo "🧹 Cleaning build cache..."
docker builder prune -f

# Increment version
source ./scripts/increment-version.sh
CURRENT_VERSION=$(cat .version)

echo "📝 Version: $CURRENT_VERSION"

# Generate environment files
echo "📝 Generating environment files..."
cd services/frontend
APP_VERSION=$CURRENT_VERSION node scripts/generate-env.js

# Load frontend .env if exists
if [ -f .env ]; then
    echo "📋 Loading frontend-specific environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Build production version
if [ -n "$SENTRY_AUTH_TOKEN" ]; then
    echo "🔨 Building with source map upload..."
    npm run build:upload
else
    echo "🔨 Building without source map upload..."
    npm run build
fi

cd ../..

# Export version for docker-compose
export APP_VERSION=$CURRENT_VERSION

# Build and start with no cache
echo "🐳 Building Docker image with no cache..."
docker-compose build --no-cache frontend

echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 15

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