"""
Universal Media Converter - A professional media conversion service.

This package provides a Flask-based web service for converting audio, video, and image files
between various formats using FFmpeg.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .app import create_app

__all__ = ["create_app"]

