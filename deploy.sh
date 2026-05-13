#!/bin/bash
# Deployment script for Dr. B.R. Ambedkar AI
# Run this on EC2 after git pull

set -e

echo "========================================="
echo "Deploying Dr. B.R. Ambedkar AI"
echo "========================================="

# Stop and remove old containers
echo "🛑 Stopping old containers..."
docker stop ambedkar-ai 2>/dev/null || true
docker rm ambedkar-ai 2>/dev/null || true

# Build new image
echo "🐳 Building Docker image..."
docker build -t ambedkar-ai .

# Run new container
echo "🚀 Starting new container..."
docker run -d \
  --name ambedkar-ai \
  -p 8000:8000 \
  --restart always \
  --env-file backend/.env \
  -v $(pwd)/backend/chroma_db:/app/chroma_db \
  ambedkar-ai

# Wait for health check
echo "⏳ Waiting for service to be ready..."
sleep 5

# Test health endpoint
echo "🔍 Testing health endpoint..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Deployment successful!"
else
    echo "❌ Deployment failed - health check not passing"
    docker logs ambedkar-ai --tail 20
    exit 1
fi

echo "========================================="
echo "✅ Dr. B.R. Ambedkar AI is running!"
echo "========================================="
