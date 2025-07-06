#!/bin/bash

echo "🧹 Cleaning up and restarting services..."

# Stop all containers
echo "Stopping containers..."
docker-compose down

# Remove any orphan containers
docker-compose rm -f

# Clean Docker build cache
echo "Cleaning Docker cache..."
docker system prune -f

# Clean frontend build cache
echo "Cleaning frontend cache..."
rm -rf services/frontend/dist
rm -rf services/frontend/.angular

# Restart based on mode
if [ "$1" = "prod" ]; then
    echo "Starting in production mode..."
    ./start-prod.sh
else
    echo "Starting in development mode..."
    ./start-dev.sh
fi