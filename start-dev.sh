#!/bin/bash

echo "🚀 Starting Sentry POC in DEVELOPMENT mode..."
echo "📝 This mode includes:"
echo "  - Source maps with full debugging"
echo "  - Hot reload for frontend"
echo "  - Debug logging enabled"
echo "  - Development environment settings"
echo ""

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