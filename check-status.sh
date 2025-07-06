#!/bin/bash

echo "🔍 Checking Sentry POC Status..."
echo ""

# Check if containers are running
echo "📦 Container Status:"
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🌐 Service Health Checks:"

# Check frontend
if curl -s -o /dev/null -w "%{http_code}" http://localhost:4200 | grep -q "200"; then
    echo "  ✅ Frontend: http://localhost:4200"
else
    echo "  ❌ Frontend: Not responding"
fi

# Check API Gateway
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/health | grep -q "200"; then
    echo "  ✅ API Gateway: http://localhost:8080"
else
    echo "  ❌ API Gateway: Not responding"
fi

echo ""
echo "📝 Quick Actions:"
echo "  - View logs: docker-compose logs -f [service-name]"
echo "  - Restart all: docker-compose restart"
echo "  - Stop all: docker-compose down"