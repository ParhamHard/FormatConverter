# 🤖 AI Agent Prompt Guide - Media Converter Service

This document is designed to help AI agents understand and work with this media converter service project.

## 🎯 Project Overview

**Project Name**: Universal Media Converter  
**Purpose**: Self-hosted media file conversion service for audio, video, and image formats  
**Technology Stack**: Python Flask + FFmpeg + Docker  
**Deployment Target**: VPS (Virtual Private Server)  

## 🏗️ Architecture

```
FormatConverter/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container definition
├── docker-compose.yml    # Docker orchestration
├── templates/
│   └── index.html        # Web UI template
├── uploads/              # Temporary file uploads
├── converted/            # Converted file outputs
├── README.md             # User documentation
└── READMEAGENT.md        # This file (AI agent reference)
```

## 🔧 Core Components

### 1. Flask Application (`app.py`)
- **Main Routes**:
  - `/` - Web interface
  - `/api/convert` - File conversion endpoint
  - `/api/download/<filename>` - File download
  - `/api/formats` - Supported formats list
  - `/api/health` - Health check

- **Key Functions**:
  - `convert_audio()` - Audio format conversion
  - `convert_video()` - Video format conversion
  - `extract_audio_from_video()` - Audio extraction
  - `convert_image()` - Image format conversion
  - `get_file_info()` - File metadata extraction

### 2. FFmpeg Integration
- **Audio Codecs**: MP3, WAV, FLAC, AAC, OGG
- **Video Codecs**: H.264, VP8, Xvid
- **Image Formats**: JPG, PNG, WebP
- **Quality Presets**: High, Medium, Low

### 3. Web Interface (`templates/index.html`)
- Drag & drop file upload
- Format selection dropdowns
- Quality settings
- Real-time progress indication
- Download links for converted files

## 📋 Supported Conversions

### Audio Formats
- **Input**: MP3, WAV, FLAC, AAC, OGG, M4A
- **Output**: MP3, WAV, FLAC, AAC, OGG
- **Special**: Audio extraction from video files

### Video Formats
- **Input**: MP4, AVI, MOV, WMV, FLV, MKV, WebM
- **Output**: MP4, AVI, MOV, WebM
- **Special**: Can extract audio from any video format

### Image Formats
- **Input**: JPG, PNG, GIF, BMP, TIFF, WebP
- **Output**: JPG, PNG, WebP
- **Features**: Quality control, compression options

## 🚀 Deployment Instructions

### Docker Deployment (Recommended)
```bash
# 1. Ensure Docker and Docker Compose are installed
docker --version
docker-compose --version

# 2. Clone and navigate to project
git clone <repository-url>
cd FormatConverter

# 3. Start service
docker-compose up -d

# 4. Verify deployment
docker-compose ps
curl http://localhost:8000/api/health
```

### Manual Deployment
```bash
# 1. Install system dependencies
sudo apt update
sudo apt install ffmpeg libavcodec-extra python3 python3-pip

# 2. Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Run service
python3 app.py
```

## 🔍 Troubleshooting Guide

### Common Issues & Solutions

1. **FFmpeg Not Found**
   ```bash
   # Check installation
   ffmpeg -version
   
   # Reinstall if needed
   sudo apt install ffmpeg libavcodec-extra
   ```

2. **Permission Errors**
   ```bash
   # Fix directory permissions
   sudo chown -R $USER:$USER uploads converted
   chmod 755 uploads converted
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   free -h
   
   # Add swap if needed
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

4. **Port Already in Use**
   ```bash
   # Check what's using port 8000
   sudo netstat -tlnp | grep :8000
   
   # Kill process or change port in app.py
   ```

### Log Analysis
```bash
# Docker logs
docker-compose logs -f converter

# Application logs (if running manually)
tail -f app.log

# System logs
sudo journalctl -u docker.service -f
```

## 🛠️ Development & Customization

### Adding New Formats
1. **Update `app.py`**:
   - Add format to `ALLOWED_EXTENSIONS`
   - Implement conversion function
   - Update format detection logic

2. **Update `templates/index.html`**:
   - Add format to dropdown options
   - Update supported formats display

3. **Update `docker-compose.yml`**:
   - Add new extensions to environment variables

### Performance Optimization
- **File Size Limits**: Adjust `MAX_FILE_SIZE` in environment
- **Quality Settings**: Modify FFmpeg parameters in conversion functions
- **Memory Usage**: Monitor and adjust Docker memory limits
- **Concurrent Users**: Implement queue system for multiple conversions

### Security Enhancements
- **File Validation**: Add virus scanning
- **Rate Limiting**: Implement API rate limiting
- **Authentication**: Add user authentication system
- **HTTPS**: Configure SSL certificates

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# API health endpoint
curl http://your-vps-ip:8000/api/health

# Docker container status
docker-compose ps

# System resources
htop
df -h
```

### Backup Strategy
```bash
# Backup configuration
cp docker-compose.yml backup/
cp .env backup/

# Backup converted files (if needed)
tar -czf converted_backup.tar.gz converted/
```

### Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## 🔗 Integration Examples

### cURL API Usage
```bash
# Convert audio file
curl -X POST -F "file=@audio.wav" -F "target_format=mp3" \
  http://your-vps-ip:8000/api/convert

# Get supported formats
curl http://your-vps-ip:8000/api/formats

# Health check
curl http://your-vps-ip:8000/api/health
```

### Python Integration
```python
import requests

# Convert file
with open('video.mp4', 'rb') as f:
    response = requests.post(
        'http://your-vps-ip:8000/api/convert',
        files={'file': f},
        data={'target_format': 'mp3'}
    )
    
if response.json()['success']:
    download_url = response.json()['download_url']
    # Download converted file...
```

## 📝 Future Enhancements

### Planned Features
- **Batch Processing**: Convert multiple files simultaneously
- **Cloud Storage**: Integration with S3, Google Drive
- **Webhook Support**: Notify external services on completion
- **Format Detection**: Automatic format recognition
- **Compression Options**: Advanced quality/compression controls

### Scalability Improvements
- **Load Balancing**: Multiple converter instances
- **Queue System**: Redis-based job queue
- **Caching**: CDN integration for converted files
- **Microservices**: Split into separate services

## 🎯 AI Agent Tasks

When working with this project, AI agents should:

1. **Understand the FFmpeg-based architecture** for media conversion
2. **Respect file size and format limitations** defined in configuration
3. **Use Docker commands** for deployment and management
4. **Check logs and health endpoints** for troubleshooting
5. **Consider security implications** when modifying file handling
6. **Test conversions** with various file types and sizes
7. **Document changes** in both README.md and READMEAGENT.md

## 📞 Support Resources

- **FFmpeg Documentation**: https://ffmpeg.org/documentation.html
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Docker Documentation**: https://docs.docker.com/
- **Project Issues**: GitHub issues page
- **Community**: Stack Overflow, Reddit r/selfhosted

---

**Last Updated**: $(date)  
**AI Agent Version**: 1.0  
**Project Status**: Production Ready
