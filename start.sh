#!/bin/bash

# Media Converter Service Startup Script

echo "🚀 Starting Media Converter Service..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if FFmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg not found. Please install FFmpeg first:"
    echo "   Ubuntu/Debian: sudo apt install ffmpeg libavcodec-extra"
    echo "   CentOS/RHEL: sudo yum install epel-release && sudo yum install ffmpeg"
    echo "   macOS: brew install ffmpeg"
    exit 1
fi

echo "✅ FFmpeg found: $(ffmpeg -version | head -n1)"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads converted temp logs

# Set permissions
chmod 755 uploads converted temp logs

# Check if running in development or production mode
if [ "$1" = "dev" ]; then
    echo "🔧 Starting in development mode..."
    export FLASK_ENV=development
    export FLASK_DEBUG=true
    python main.py
else
    echo "🚀 Starting in production mode..."
    export FLASK_ENV=production
    export FLASK_DEBUG=false
    
    # Check if gunicorn is available
    if command -v gunicorn &> /dev/null; then
        echo "🐳 Starting with Gunicorn..."
        gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 300 src.wsgi:app
    else
        echo "🐍 Starting with Flask development server..."
        python main.py
    fi
fi
