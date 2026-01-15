#!/usr/bin/env bash

PROJECT_NAME=$(uv version | awk '{print $1}')
VERSION=$(uv version | awk '{print $2}')

if [ -z "$PROJECT_NAME" ] || [ -z "$VERSION" ]; then
    echo "Error: Could not extract project info from pyproject.toml"
    exit 1
fi

IMAGE_NAME="${PROJECT_NAME}:${VERSION}"
LATEST_TAG="${PROJECT_NAME}:latest"

echo "------------------------------------------"
echo "Building Docker Image: $IMAGE_NAME"
echo "------------------------------------------"

docker build -t "$IMAGE_NAME" -t "$LATEST_TAG" .

if [ $? -eq 0 ]; then
    echo ""
    echo "Successfully built: $IMAGE_NAME"
    echo "Successfully tagged: $LATEST_TAG"
    echo ""
    echo "To run the container:"
    echo "docker run -p 8000:8000 $LATEST_TAG"
else
    echo "Build failed!"
    exit 1
fi