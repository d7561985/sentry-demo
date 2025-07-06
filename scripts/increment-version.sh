#!/bin/bash

VERSION_FILE=".version"

# Read current version
if [ -f "$VERSION_FILE" ]; then
    CURRENT_VERSION=$(cat "$VERSION_FILE")
else
    CURRENT_VERSION="1.0.0"
fi

# Parse version parts
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Increment patch version
PATCH=$((PATCH + 1))

# Create new version
NEW_VERSION="$MAJOR.$MINOR.$PATCH"

# Save new version
echo "$NEW_VERSION" > "$VERSION_FILE"

echo "Version incremented from $CURRENT_VERSION to $NEW_VERSION"

# Export for use in other scripts
export APP_VERSION="$NEW_VERSION"