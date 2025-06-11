#!/bin/bash

set -e

# Configuration
VOLUME_NAME="crawler_data"
TARGET_DIR="crawler/data/docker"
COMPOSE_PROJECT=$(basename "$PWD")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Docker Volume Data Dump Script${NC}"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running or not accessible${NC}"
    exit 1
fi

# Get the full volume name (with compose project prefix)
FULL_VOLUME_NAME="${COMPOSE_PROJECT}_${VOLUME_NAME}"

# Check if volume exists
if ! docker volume inspect "$FULL_VOLUME_NAME" > /dev/null 2>&1; then
    echo -e "${RED}Error: Volume '$FULL_VOLUME_NAME' does not exist${NC}"
    echo "Available volumes:"
    docker volume ls | grep "$COMPOSE_PROJECT" || echo "No volumes found for project '$COMPOSE_PROJECT'"
    exit 1
fi

echo -e "${YELLOW}Volume found: $FULL_VOLUME_NAME${NC}"

# Clean target directory
echo -e "${YELLOW}Cleaning target directory: $TARGET_DIR${NC}"
if [ -d "$TARGET_DIR" ]; then
    rm -rf "$TARGET_DIR"
    echo -e "${GREEN}Target directory cleaned${NC}"
fi

# Create target directory
mkdir -p "$TARGET_DIR"
echo -e "${GREEN}Target directory created: $TARGET_DIR${NC}"

# Dump volume contents using a temporary container
echo -e "${YELLOW}Dumping volume contents...${NC}"

# Use alpine image to copy data from volume to host
CONTAINER_ID=$(docker run -d \
    --rm \
    -v "$FULL_VOLUME_NAME:/source:ro" \
    -v "$(pwd)/$TARGET_DIR:/target" \
    alpine:latest \
    sh -c "
        echo 'Copying volume contents...' &&
        if [ -d /source ] && [ \"\$(ls -A /source 2>/dev/null)\" ]; then
            cp -r /source/* /target/ 2>/dev/null || true
            cp -r /source/.[!.]* /target/ 2>/dev/null || true
            echo 'Volume contents copied successfully'
        else
            echo 'Source volume is empty or does not exist'
        fi &&
        echo 'Setting proper permissions...' &&
        chown -R $(id -u):$(id -g) /target 2>/dev/null || true &&
        echo 'Permissions set successfully'
    ")

# Wait for the container to finish
docker wait "$CONTAINER_ID" > /dev/null

# Check if copy was successful
if [ "$(ls -A "$TARGET_DIR" 2>/dev/null)" ]; then
    echo -e "${GREEN}✓ Volume dump completed successfully${NC}"
    echo -e "${GREEN}Data location: $TARGET_DIR${NC}"

    # Show summary of copied data
    echo -e "\n${YELLOW}Summary of dumped data:${NC}"
    echo "Directory: $TARGET_DIR"
    echo "Size: $(du -sh "$TARGET_DIR" 2>/dev/null | cut -f1 || echo 'Unknown')"
    echo "Files count: $(find "$TARGET_DIR" -type f 2>/dev/null | wc -l || echo 'Unknown')"

    # Show top-level contents
    echo -e "\n${YELLOW}Top-level contents:${NC}"
    ls -la "$TARGET_DIR" 2>/dev/null || echo "Unable to list contents"

else
    echo -e "${YELLOW}⚠ Volume appears to be empty or dump failed${NC}"
    echo "Target directory: $TARGET_DIR"
fi

echo -e "\n${GREEN}Script completed${NC}"
