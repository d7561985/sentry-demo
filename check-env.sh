#!/bin/bash

# Script to check environment configuration

echo "🔍 Checking environment configuration..."
echo ""

# Check main .env file
if [ -f .env ]; then
    echo "✅ Main .env file found"
    
    # Load environment variables
    export $(cat .env | grep -v '^#' | xargs)
    
    # Check Sentry DSNs
    echo ""
    echo "📊 Sentry DSNs:"
    if [ -n "$SENTRY_FRONTEND_DSN" ] && [ "$SENTRY_FRONTEND_DSN" != "https://YOUR_KEY@o123456.ingest.sentry.io/1234567" ]; then
        echo "  ✅ Frontend DSN configured"
    else
        echo "  ❌ Frontend DSN not configured"
    fi
    
    if [ -n "$SENTRY_GATEWAY_DSN" ] && [ "$SENTRY_GATEWAY_DSN" != "https://YOUR_KEY@o123456.ingest.sentry.io/1234568" ]; then
        echo "  ✅ Gateway DSN configured"
    else
        echo "  ❌ Gateway DSN not configured"
    fi
    
    # Check other DSNs similarly...
    
else
    echo "❌ Main .env file not found"
    echo "   Run: cp .env.example .env"
fi

echo ""

# Check frontend .env file
if [ -f services/frontend/.env ]; then
    echo "✅ Frontend .env file found"
    
    # Load frontend environment variables
    export $(cat services/frontend/.env | grep -v '^#' | xargs)
    
    echo ""
    echo "📦 Frontend Source Map Configuration:"
    if [ -n "$SENTRY_ORG" ] && [ "$SENTRY_ORG" != "your-org" ]; then
        echo "  ✅ SENTRY_ORG: $SENTRY_ORG"
    else
        echo "  ❌ SENTRY_ORG not configured"
    fi
    
    if [ -n "$SENTRY_PROJECT" ] && [ "$SENTRY_PROJECT" != "igaming-frontend" ]; then
        echo "  ✅ SENTRY_PROJECT: $SENTRY_PROJECT"
    else
        echo "  ⚠️  SENTRY_PROJECT: $SENTRY_PROJECT (using default)"
    fi
    
    if [ -n "$SENTRY_AUTH_TOKEN" ] && [ "$SENTRY_AUTH_TOKEN" != "your-auth-token" ]; then
        echo "  ✅ SENTRY_AUTH_TOKEN configured (hidden)"
    else
        echo "  ❌ SENTRY_AUTH_TOKEN not configured"
    fi
else
    echo "⚠️  Frontend .env file not found"
    echo "   Source maps will not be uploaded"
    echo "   To enable: cd services/frontend && cp .env.example .env"
fi

echo ""
echo "💡 Tips:"
echo "   - Main .env contains Sentry DSNs for all services"
echo "   - Frontend .env contains auth token for source map upload"
echo "   - Both files are needed for full functionality"