"""
Configuration management for the Media Converter service.
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Config:
    """Application configuration."""
    
    # Flask settings
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG: bool = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # File handling
    MAX_FILE_SIZE: int = int(os.environ.get('MAX_FILE_SIZE', '500MB').replace('MB', '')) * 1024 * 1024
    UPLOAD_FOLDER: str = os.environ.get('UPLOAD_FOLDER', 'uploads')
    CONVERTED_FOLDER: str = os.environ.get('CONVERTED_FOLDER', 'converted')
    TEMP_FOLDER: str = os.environ.get('TEMP_FOLDER', 'temp')
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS: List[str] = None  # Will be set in __post_init__
    
    # FFmpeg settings
    FFMPEG_PATH: str = os.environ.get('FFMPEG_PATH', 'ffmpeg')
    FFPROBE_PATH: str = os.environ.get('FFPROBE_PATH', 'ffprobe')
    
    # Quality presets
    AUDIO_QUALITY_PRESETS: Dict[str, str] = field(default_factory=lambda: {
        'low': '128k',
        'medium': '192k', 
        'high': '320k'
    })
    
    VIDEO_QUALITY_PRESETS: Dict[str, str] = field(default_factory=lambda: {
        'low': '23',
        'medium': '20',
        'high': '18'
    })
    
    # Server settings
    HOST: str = os.environ.get('HOST', '0.0.0.0')
    PORT: int = int(os.environ.get('PORT', '8000'))
    
    # Logging
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # Security
    ALLOWED_HOSTS: List[str] = None  # Will be set in __post_init__
    RATE_LIMIT: str = os.environ.get('RATE_LIMIT', '100 per minute')
    
    def __post_init__(self):
        """Ensure directories exist after initialization."""
        # Set ALLOWED_EXTENSIONS if not already set
        if self.ALLOWED_EXTENSIONS is None:
            self.ALLOWED_EXTENSIONS = os.environ.get(
                'ALLOWED_EXTENSIONS', 
                'mp3,wav,flac,aac,ogg,m4a,mp4,avi,mov,wmv,flv,mkv,webm,jpg,jpeg,png,gif,bmp,tiff,webp'
            ).split(',')
        
        # Set ALLOWED_HOSTS if not already set
        if self.ALLOWED_HOSTS is None:
            self.ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')
        
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(self.CONVERTED_FOLDER, exist_ok=True)
        os.makedirs(self.TEMP_FOLDER, exist_ok=True)
        os.makedirs(os.path.dirname(self.LOG_FILE), exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    UPLOAD_FOLDER = 'test_uploads'
    CONVERTED_FOLDER = 'test_converted'
    TEMP_FOLDER = 'test_temp'


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Config:
    """Get configuration instance."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])()

