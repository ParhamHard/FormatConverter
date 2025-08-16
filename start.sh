#!/bin/bash

# Universal Media Converter Startup Script

echo "🎵 Starting Universal Media Converter..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it first."
    exit 1
fi

# Create necessary directories
mkdir -p uploads converted

# Start the service
echo "🚀 Starting service with Docker Compose..."
docker-compose up -d

# Wait a moment for the service to start
sleep 5

# Check if service is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Service is running successfully!"
    echo "🌐 Web Interface: http://localhost:8000"
    echo "🔍 Health Check: http://localhost:8000/api/health"
    echo "📋 Supported Formats: http://localhost:8000/api/formats"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
else
    echo "❌ Service failed to start. Check logs with: docker-compose logs"
    exit 1
fi
