"""
Tests for converter classes.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from src.config import TestingConfig
from src.converters import AudioConverter, VideoConverter, ImageConverter


@pytest.fixture
def test_config():
    """Create test configuration."""
    return TestingConfig()


@pytest.fixture
def temp_dir():
    """Create temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


class TestAudioConverter:
    """Test AudioConverter class."""
    
    def test_init(self, test_config):
        """Test AudioConverter initialization."""
        converter = AudioConverter(test_config)
        assert converter.config == test_config
        assert 'mp3' in converter.supported_formats
    
    def test_get_supported_formats(self, test_config):
        """Test getting supported formats."""
        converter = AudioConverter(test_config)
        formats = converter.get_supported_formats()
        assert 'mp3' in formats
        assert 'wav' in formats
        assert 'flac' in formats


class TestVideoConverter:
    """Test VideoConverter class."""
    
    def test_init(self, test_config):
        """Test VideoConverter initialization."""
        converter = VideoConverter(test_config)
        assert converter.config == test_config
        assert 'mp4' in converter.supported_formats
    
    def test_get_supported_formats(self, test_config):
        """Test getting supported formats."""
        converter = VideoConverter(test_config)
        formats = converter.get_supported_formats()
        assert 'mp4' in formats
        assert 'avi' in formats
        assert 'webm' in formats


class TestImageConverter:
    """Test ImageConverter class."""
    
    def test_init(self, test_config):
        """Test ImageConverter initialization."""
        converter = ImageConverter(test_config)
        assert converter.config == test_config
        assert 'jpg' in converter.supported_formats
    
    def test_get_supported_formats(self, test_config):
        """Test getting supported formats."""
        converter = ImageConverter(test_config)
        formats = converter.get_supported_formats()
        assert 'jpg' in formats
        assert 'png' in formats
        assert 'webp' in formats


class TestBaseConverter:
    """Test BaseConverter functionality through concrete implementations."""
    
    def test_validate_input_file_nonexistent(self, test_config):
        """Test input file validation with nonexistent file."""
        converter = AudioConverter(test_config)
        is_valid, error_msg = converter.validate_input_file('/nonexistent/file.mp3')
        assert not is_valid
        assert 'not found' in error_msg
    
    def test_validate_output_path(self, test_config, temp_dir):
        """Test output path validation."""
        converter = AudioConverter(test_config)
        output_path = os.path.join(temp_dir, 'test.mp3')
        is_valid, error_msg = converter.validate_output_path(output_path)
        assert is_valid
        assert error_msg == ""
