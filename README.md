# 🎵 Universal Media Converter

A powerful, self-hosted media conversion service that can convert audio, video, and image files between various formats. Built with Python Flask and FFmpeg for maximum compatibility and quality.

## ✨ Features

- **Audio Conversion**: MP3, WAV, FLAC, AAC, OGG, M4A
- **Video Conversion**: MP4, AVI, MOV, WMV, FLV, MKV, WebM
- **Image Conversion**: JPG, PNG, GIF, BMP, TIFF, WebP
- **Audio Extraction**: Extract audio from video files
- **Quality Control**: Multiple quality presets for optimal file size/quality balance
- **Modern Web UI**: Drag & drop interface with real-time progress
- **RESTful API**: Easy integration with other services
- **Docker Support**: One-command deployment

## 🚀 Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed on your VPS
- At least 2GB RAM and 10GB storage

### 1. Clone and Deploy
```bash
# Clone the repository
git clone <your-repo-url>
cd FormatConverter

# Start the service
docker-compose up -d

# Check status
docker-compose ps
```

### 2. Access the Service
- **Web Interface**: http://your-vps-ip:8000
- **API Health Check**: http://your-vps-ip:8000/api/health
- **Supported Formats**: http://your-vps-ip:8000/api/formats

## 🛠️ Manual Installation

### Prerequisites
- Python 3.8+
- FFmpeg with codecs
- 2GB+ RAM

### 1. Install FFmpeg
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg libavcodec-extra

# CentOS/RHEL
sudo yum install epel-release
sudo yum install ffmpeg ffmpeg-devel

# macOS
brew install ffmpeg
```

### 2. Install Python Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Service
```bash
python3 app.py
```

## 📁 API Endpoints

### Convert File
```http
POST /api/convert
Content-Type: multipart/form-data

Parameters:
- file: File to convert
- target_format: Desired output format
- quality: high/medium/low (optional)
```

### Download Converted File
```http
GET /api/download/{filename}
```

### Get Supported Formats
```http
GET /api/formats
```

### Health Check
```http
GET /api/health
```

## 🔧 Configuration

### Environment Variables
```bash
MAX_FILE_SIZE=500MB          # Maximum file size limit
ALLOWED_EXTENSIONS=mp3,wav,mp4,avi,jpg,png  # Allowed file extensions
```

### Docker Configuration
```yaml
# docker-compose.yml
environment:
  - MAX_FILE_SIZE=500MB
  - ALLOWED_EXTENSIONS=mp3,wav,flac,aac,ogg,m4a,mp4,avi,mov,wmv,flv,mkv,webm,jpg,jpeg,png,gif,bmp,tiff,webp
```

## 📊 Supported Conversions

### Audio Formats
| From/To | MP3 | WAV | FLAC | AAC | OGG | M4A |
|---------|-----|-----|------|-----|-----|-----|
| MP3     | ✅  | ✅  | ✅   | ✅  | ✅  | ✅  |
| WAV     | ✅  | ✅  | ✅   | ✅  | ✅  | ✅  |
| FLAC    | ✅  | ✅  | ✅   | ✅  | ✅  | ✅  |
| AAC     | ✅  | ✅  | ✅   | ✅  | ✅  | ✅  |
| OGG     | ✅  | ✅  | ✅   | ✅  | ✅  | ✅  |
| M4A     | ✅  | ✅  | ✅   | ✅  | ✅  | ✅  |

### Video Formats
| From/To | MP4 | AVI | MOV | WebM |
|---------|-----|-----|-----|------|
| MP4     | ✅  | ✅  | ✅  | ✅   |
| AVI     | ✅  | ✅  | ✅  | ✅   |
| MOV     | ✅  | ✅  | ✅  | ✅   |
| WebM    | ✅  | ✅  | ✅  | ✅   |

### Image Formats
| From/To | JPG | PNG | WebP |
|---------|-----|-----|------|
| JPG     | ✅  | ✅  | ✅   |
| PNG     | ✅  | ✅  | ✅   |
| WebP    | ✅  | ✅  | ✅   |

## 🎯 Use Cases

- **Podcast Production**: Convert various audio formats to MP3
- **Video Editing**: Convert between video formats for editing software
- **Web Optimization**: Convert images to WebP for faster loading
- **Audio Extraction**: Extract audio from video files for music
- **Format Standardization**: Convert files to standard formats for compatibility

## 🔒 Security Features

- File type validation
- File size limits
- Temporary file cleanup
- Unique filename generation
- No persistent file storage

## 📈 Performance

- **Small Files (<10MB)**: <5 seconds
- **Medium Files (10-100MB)**: 5-30 seconds
- **Large Files (100-500MB)**: 30 seconds - 5 minutes

*Performance depends on VPS specifications and file complexity*

## 🐛 Troubleshooting

### Common Issues

1. **FFmpeg not found**
   ```bash
   # Check if FFmpeg is installed
   ffmpeg -version
   
   # Reinstall if needed
   sudo apt install ffmpeg
   ```

2. **Permission denied**
   ```bash
   # Fix directory permissions
   sudo chown -R $USER:$USER uploads converted
   chmod 755 uploads converted
   ```

3. **Out of memory**
   ```bash
   # Increase swap space
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### Logs
```bash
# Docker logs
docker-compose logs -f converter

# Application logs
tail -f app.log
```

## 🚀 Production Deployment

### 1. Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeouts for large files
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

### 2. SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Systemd Service (Alternative to Docker)
```ini
# /etc/systemd/system/media-converter.service
[Unit]
Description=Media Converter Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/FormatConverter
Environment=PATH=/path/to/FormatConverter/venv/bin
ExecStart=/path/to/FormatConverter/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FFmpeg**: The backbone of all media conversion
- **Flask**: Web framework for the API
- **Docker**: Containerization for easy deployment

## 📞 Support

- **Issues**: Create a GitHub issue
- **Documentation**: Check this README
- **Community**: Join our discussions

---

**Made with ❤️ for self-hosted media conversion**
