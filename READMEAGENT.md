# 🤖 AI Agent Prompt Guide - Media Converter Service (Restructured)

This document is designed to help AI agents understand and work with the **restructured** media converter service project.

## 🎯 Project Overview

**Project Name**: Media Converter Service  
**Purpose**: Professional, self-hosted media file conversion service for audio, video, and image formats  
**Technology Stack**: Python Flask + FFmpeg + Docker + Modern Python Architecture  
**Deployment Target**: VPS (Virtual Private Server) or local development  
**Architecture**: Clean, modular, production-ready Python package structure  

## 🏗️ New Architecture (Restructured)

```
FormatConverter/
├── src/                           # Main source code package
│   ├── __init__.py               # Package initialization
│   ├── app.py                    # Flask application factory
│   ├── wsgi.py                   # Production WSGI entry point
│   ├── __main__.py               # Module execution entry point
│   ├── cli.py                    # Command-line interface
│   ├── config.py                 # Configuration management
│   ├── converters/               # Media conversion modules
│   │   ├── __init__.py
│   │   ├── base_converter.py     # Abstract base converter
│   │   ├── audio_converter.py    # Audio conversion logic
│   │   ├── video_converter.py    # Video conversion logic
│   │   └── image_converter.py    # Image conversion logic
│   ├── routes/                   # Route blueprints
│   │   ├── __init__.py
│   │   ├── api.py                # API endpoints
│   │   └── web.py                # Web interface routes
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       ├── file_utils.py         # File operations
│       └── ffmpeg_utils.py       # FFmpeg utilities
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   └── test_converters.py        # Converter tests
├── templates/                    # HTML templates
├── uploads/                      # Temporary file uploads
├── converted/                    # Converted file outputs
├── temp/                         # Temporary processing files
├── logs/                         # Application logs
├── main.py                       # Development entry point
├── setup.py                      # Package installation
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker container definition
├── docker-compose.yml            # Docker orchestration
├── start.sh                      # Startup script
├── env.example                   # Environment variables template
├── README.md                     # User documentation
└── READMEAGENT.md                # This file (AI agent reference)
```

## 🔧 Core Components (Restructured)

### 1. Application Factory (`src/app.py`)
- **Factory Pattern**: `create_app()` function for application creation
- **Configuration Management**: Environment-based configuration loading
- **Blueprint Registration**: Modular route organization
- **Error Handling**: Comprehensive error handlers
- **Logging Setup**: Production-ready logging configuration
- **Health Checks**: Built-in health monitoring

### 2. Configuration System (`src/config.py`)
- **Environment-Based**: Multiple configuration classes (dev, prod, test)
- **Type Safety**: Dataclass-based configuration with validation
- **Automatic Setup**: Directory creation and permission handling
- **Flexible**: Easy to extend and customize

### 3. Converter Architecture (`src/converters/`)
- **Base Class**: `BaseConverter` abstract base class
- **Specialized Converters**: Audio, Video, Image converters
- **Error Handling**: Comprehensive error handling and cleanup
- **Validation**: Input/output validation and file checking
- **Logging**: Detailed conversion logging and statistics

### 4. Route Organization (`src/routes/`)
- **Blueprint Pattern**: Modular route organization
- **API Routes**: RESTful API endpoints with proper error handling
- **Web Routes**: Web interface routes
- **Validation**: Request validation and sanitization

### 5. Utility Modules (`src/utils/`)
- **File Operations**: File handling, validation, and cleanup
- **FFmpeg Integration**: FFmpeg availability checking and utilities
- **Type Hints**: Full type annotation support

### 6. CLI Interface (`src/cli.py`)
- **Click Framework**: Professional command-line interface
- **Multiple Commands**: Convert, extract-audio, resize, info, formats
- **Configuration Support**: Environment-based configuration
- **Error Handling**: Comprehensive error reporting

## 📋 Supported Conversions (Enhanced)

### Audio Formats
- **Input**: MP3, WAV, FLAC, AAC, OGG, M4A
- **Output**: MP3, WAV, FLAC, AAC, OGG
- **Special Features**: 
  - Audio extraction from video files
  - Audio normalization
  - Quality presets (low, medium, high)
  - Custom bitrate and sample rate

### Video Formats
- **Input**: MP4, AVI, MOV, WMV, FLV, MKV, WebM
- **Output**: MP4, AVI, MOV, WebM, MKV
- **Special Features**:
  - Frame extraction
  - Thumbnail creation
  - Video compression to target size
  - Quality presets with CRF values

### Image Formats
- **Input**: JPG, PNG, GIF, BMP, TIFF, WebP
- **Output**: JPG, PNG, WebP
- **Special Features**:
  - Image resizing with aspect ratio preservation
  - Compression to target file size
  - Thumbnail generation
  - Quality control

## 🚀 Deployment Instructions (Updated)

### 1. Local Development
```bash
# Clone and setup
git clone <repository-url>
cd FormatConverter

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development server
./start.sh dev
# or
python main.py
```

### 2. Production Deployment
```bash
# Install as package
pip install -e .

# Start production server
./start.sh
# or
gunicorn --bind 0.0.0.0:8000 --workers 4 src.wsgi:app
```

### 3. Docker Deployment (Recommended)
```bash
# Build and start
docker-compose up -d --build

# Check status
docker-compose ps
docker-compose logs -f converter
```

### 4. CLI Usage
```bash
# Check system requirements
python -m src check

# Convert file
python -m src convert input.mp3 output.wav --format wav --quality high

# Extract audio from video
python -m src extract-audio video.mp4 audio.mp3 --format mp3

# Resize image
python -m src resize image.jpg resized.jpg --width 800 --height 600

# Get file info
python -m src info file.mp3

# Show supported formats
python -m src formats
```

## 🔍 Troubleshooting Guide (Enhanced)

### Common Issues & Solutions

1. **Import Errors**
   ```bash
   # Ensure you're in the project root
   cd FormatConverter
   
   # Install in development mode
   pip install -e .
   
   # Or use the main.py entry point
   python main.py
   ```

2. **Configuration Issues**
   ```bash
   # Copy environment template
   cp env.example .env
   
   # Edit .env with your settings
   nano .env
   
   # Check configuration
   python -m src check
   ```

3. **FFmpeg Issues**
   ```bash
   # Check FFmpeg availability
   python -m src check
   
   # Install FFmpeg
   sudo apt install ffmpeg libavcodec-extra
   ```

4. **Permission Issues**
   ```bash
   # Fix directory permissions
   sudo chown -R $USER:$USER uploads converted temp logs
   chmod 755 uploads converted temp logs
   ```

### Log Analysis
```bash
# Application logs
tail -f logs/app.log

# Docker logs
docker-compose logs -f converter

# CLI verbose output
python -m src convert input.mp3 output.wav --verbose
```

## 🛠️ Development & Customization (Enhanced)

### Adding New Converters
1. **Create Converter Class**:
   ```python
   # src/converters/new_converter.py
   from .base_converter import BaseConverter
   
   class NewConverter(BaseConverter):
       def __init__(self, config):
           super().__init__(config)
           self.supported_formats = ['format1', 'format2']
       
       def convert(self, input_path, output_path, target_format, quality='medium', **kwargs):
           # Implementation here
           pass
   ```

2. **Update Package**:
   ```python
   # src/converters/__init__.py
   from .new_converter import NewConverter
   
   __all__ = [..., 'NewConverter']
   ```

3. **Add Routes**:
   ```python
   # src/routes/api.py
   from ..converters import NewConverter
   
   # Add conversion logic in convert_file route
   ```

### Testing
```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_converters.py::TestAudioConverter
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## 📊 Monitoring & Maintenance (Enhanced)

### Health Checks
```bash
# API health endpoint
curl http://your-vps-ip:8000/health

# CLI health check
python -m src check

# Docker health check
docker-compose ps
```

### Performance Monitoring
```bash
# Check conversion statistics
tail -f logs/app.log | grep "Conversion completed"

# Monitor file sizes
du -sh uploads/ converted/ temp/

# Check system resources
htop
df -h
```

## 🔗 Integration Examples (Enhanced)

### Python API Usage
```python
import requests

# Convert file
with open('video.mp4', 'rb') as f:
    response = requests.post(
        'http://your-vps-ip:8000/api/convert',
        files={'file': f},
        data={'target_format': 'mp3', 'extract_audio': 'true'}
    )
    
if response.json()['success']:
    download_url = response.json()['download_url']
    # Download converted file...
```

### CLI Integration
```bash
# Batch conversion script
for file in *.mp3; do
    python -m src convert "$file" "${file%.mp3}.wav" --format wav --quality high
done
```

## 📝 Future Enhancements (Planned)

### Planned Features
- **Batch Processing**: Convert multiple files simultaneously
- **Queue System**: Redis-based job queue for scalability
- **Cloud Storage**: S3, Google Drive integration
- **Webhook Support**: Notify external services on completion
- **Format Detection**: Automatic format recognition
- **Compression Options**: Advanced quality/compression controls

### Scalability Improvements
- **Load Balancing**: Multiple converter instances
- **Microservices**: Split into separate services
- **Caching**: CDN integration for converted files
- **Monitoring**: Prometheus metrics and Grafana dashboards

## 🎯 AI Agent Tasks (Updated)

When working with this **restructured** project, AI agents should:

1. **Understand the new modular architecture** with proper separation of concerns
2. **Use the factory pattern** (`create_app()`) for application creation
3. **Respect the converter hierarchy** (BaseConverter → specialized converters)
4. **Follow the blueprint pattern** for route organization
5. **Use the CLI interface** for testing and debugging
6. **Check configuration classes** for environment-specific settings
7. **Test with the new test suite** structure
8. **Document changes** in both README.md and READMEAGENT.md
9. **Use type hints** throughout the codebase
10. **Follow the new logging and error handling patterns**

## 📞 Support Resources

- **FFmpeg Documentation**: https://ffmpeg.org/documentation.html
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Click Documentation**: https://click.palletsprojects.com/
- **Docker Documentation**: https://docs.docker.com/
- **Project Issues**: GitHub issues page
- **Community**: Stack Overflow, Reddit r/selfhosted

---

**Last Updated**: $(date)  
**AI Agent Version**: 2.0 (Restructured)  
**Project Status**: Production Ready with Professional Architecture
