#!/bin/bash

# Script for uploading source maps to Sentry
# Compatible with Sentry SDK v7

RELEASE_VERSION=${1:-"1.0.0"}
SENTRY_ORG=${SENTRY_ORG:-"your-org"}
SENTRY_PROJECT=${SENTRY_PROJECT:-"igaming-frontend"}

echo "📦 Uploading source maps to Sentry..."
echo "Release: $RELEASE_VERSION"

# Ensure we have auth token
if [ -z "$SENTRY_AUTH_TOKEN" ]; then
  echo "❌ Error: SENTRY_AUTH_TOKEN not set"
  echo "Get your token from: https://sentry.io/settings/account/api/auth-tokens/"
  exit 1
fi

# Create release
echo "Creating release..."
npx @sentry/cli releases new $RELEASE_VERSION

# Upload source maps
echo "Uploading source maps..."
npx @sentry/cli releases files $RELEASE_VERSION upload-sourcemaps ./dist/frontend \
  --url-prefix '~/' \
  --rewrite \
  --validate

# Finalize release
echo "Finalizing release..."
npx @sentry/cli releases finalize $RELEASE_VERSION

echo "✅ Source maps uploaded successfully!"