#!/bin/bash

# Script to upload source maps from Docker container after build
# This ensures we upload the exact same files that are deployed

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Get current version
CURRENT_VERSION=$(cat .version)

echo "📦 Uploading source maps from Docker container..."
echo "   Version: $CURRENT_VERSION"
echo "   Container: sentry-poc-frontend"

# Check if container is running
if ! docker ps | grep -q sentry-poc-frontend; then
    echo "❌ Error: Frontend container is not running"
    echo "   Run ./start-prod.sh first"
    exit 1
fi

# Ensure we have auth token
if [ -z "$SENTRY_AUTH_TOKEN" ]; then
    echo "❌ Error: SENTRY_AUTH_TOKEN not set"
    echo "   Set it in .env file"
    exit 1
fi

# Create a temporary directory
TEMP_DIR=$(mktemp -d)
echo "📁 Using temporary directory: $TEMP_DIR"

# Copy files from container
echo "📥 Copying files from container..."
docker cp sentry-poc-frontend:/usr/share/nginx/html/browser $TEMP_DIR/

# Upload source maps with version
echo "📤 Uploading source maps to Sentry..."
cd $TEMP_DIR

npx @sentry/cli sourcemaps upload \
  --org "$SENTRY_ORG" \
  --project "$SENTRY_PROJECT" \
  --release "$CURRENT_VERSION" \
  ./browser

# Clean up
cd - > /dev/null
rm -rf $TEMP_DIR

echo "✅ Source maps uploaded successfully from deployed container!"
echo "   Version: $CURRENT_VERSION"
echo "   Files were taken directly from the running container"