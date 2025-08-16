"""
Pytest configuration and fixtures.
"""

import pytest
import tempfile
import os
from src.config import TestingConfig


@pytest.fixture(scope="session")
def test_config():
    """Create test configuration for the test session."""
    return TestingConfig()


@pytest.fixture(scope="function")
def temp_dir():
    """Create temporary directory for each test."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(scope="function")
def sample_audio_file(temp_dir):
    """Create a sample audio file for testing."""
    # This would create a minimal audio file for testing
    # In practice, you might want to use a real small audio file
    sample_path = os.path.join(temp_dir, "sample.mp3")
    with open(sample_path, "wb") as f:
        # Write minimal MP3 header
        f.write(b'\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    return sample_path


@pytest.fixture(scope="function")
def sample_image_file(temp_dir):
    """Create a sample image file for testing."""
    # This would create a minimal image file for testing
    # In practice, you might want to use a real small image file
    sample_path = os.path.join(temp_dir, "sample.jpg")
    with open(sample_path, "wb") as f:
        # Write minimal JPEG header
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00')
    return sample_path
