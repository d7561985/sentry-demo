#!/bin/bash

echo "🔍 Checking versions across the system..."
echo ""

# Check .version file
echo "📄 .version file: $(cat .version)"
echo ""

# Check environment variable
echo "🌍 APP_VERSION env: ${APP_VERSION:-not set}"
echo ""

# Check versions in running containers
echo "📦 Container versions:"

# Frontend
if docker ps | grep -q sentry-poc-frontend; then
    echo -n "  Frontend: "
    docker exec sentry-poc-frontend sh -c 'grep -o "version:\"[^\"]*\"" /usr/share/nginx/html/browser/main*.js 2>/dev/null | head -1 | cut -d":" -f2 | tr -d "\""' || echo "not found"
fi

# API Gateway
if docker ps | grep -q sentry-poc-gateway; then
    echo -n "  API Gateway: "
    docker exec sentry-poc-gateway printenv APP_VERSION 2>/dev/null || echo "not set"
fi

# User Service
if docker ps | grep -q sentry-poc-user; then
    echo -n "  User Service: "
    docker exec sentry-poc-user printenv APP_VERSION 2>/dev/null || echo "not set"
fi

# Game Engine
if docker ps | grep -q sentry-poc-game; then
    echo -n "  Game Engine: "
    docker exec sentry-poc-game printenv APP_VERSION 2>/dev/null || echo "not set"
fi

# Analytics Service
if docker ps | grep -q sentry-poc-analytics; then
    echo -n "  Analytics: "
    docker exec sentry-poc-analytics printenv APP_VERSION 2>/dev/null || echo "not set"
fi

echo ""
echo "💡 Tip: All versions should match the .version file"