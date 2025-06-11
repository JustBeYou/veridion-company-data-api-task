#!/bin/bash

# Fix Docker volume permissions for the crawler data

echo "Fixing Docker volume permissions..."

# Stop services if running
echo "Stopping services..."
docker-compose down

# Remove existing volume (WARNING: This will delete all data)
read -p "WARNING: This will delete all crawler data. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operation cancelled."
    exit 1
fi

echo "Removing existing volume..."
docker-compose down -v

# Start the volume initialization
echo "Initializing volume with proper permissions..."
docker-compose up volume-init

# Start all services
echo "Starting all services..."
docker-compose up -d

echo "Permission fix complete!"
echo "Dashboard available at: http://localhost:5000"
echo ""
echo "Monitor logs with: docker-compose logs -f"
