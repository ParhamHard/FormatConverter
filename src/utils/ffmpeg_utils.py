"""
FFmpeg utility functions for the Media Converter service.
"""

import subprocess
import logging
from typing import Tuple, Optional, Dict, Any
from pathlib import Path


def check_ffmpeg_available() -> Tuple[bool, str]:
    """
    Check if FFmpeg is available on the system.
    
    Returns:
        Tuple of (is_available, error_message)
    """
    try:
        # Check ffmpeg
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return False, "FFmpeg command failed"
        
        # Check ffprobe
        result = subprocess.run(['ffprobe', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return False, "FFprobe command failed"
        
        return True, ""
        
    except FileNotFoundError:
        return False, "FFmpeg not found in PATH"
    except subprocess.TimeoutExpired:
        return False, "FFmpeg command timed out"
    except Exception as e:
        return False, f"Error checking FFmpeg: {str(e)}"


def get_ffmpeg_version() -> Optional[str]:
    """
    Get FFmpeg version information.
    
    Returns:
        FFmpeg version string or None if unavailable
    """
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            if lines:
                return lines[0].strip()
    except Exception:
        pass
    return None


def validate_ffmpeg_command(cmd: list, timeout: int = 300) -> Tuple[bool, str, str]:
    """
    Validate an FFmpeg command by running it with a test file.
    
    Args:
        cmd: FFmpeg command list
        timeout: Command timeout in seconds
        
    Returns:
        Tuple of (success, stdout, stderr)
    """
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def get_supported_formats() -> Dict[str, list]:
    """
    Get supported input and output formats from FFmpeg.
    
    Returns:
        Dictionary with 'input' and 'output' format lists
    """
    formats = {'input': [], 'output': []}
    
    try:
        # Get input formats
        result = subprocess.run(['ffmpeg', '-formats'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith(' D'):
                    parts = line.split()
                    if len(parts) >= 2:
                        formats['input'].append(parts[1])
        
        # Get output formats
        result = subprocess.run(['ffmpeg', '-formats'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('DE'):
                    parts = line.split()
                    if len(parts) >= 2:
                        formats['output'].append(parts[1])
                        
    except Exception as e:
        logging.error(f"Error getting supported formats: {e}")
    
    return formats


def get_codec_info() -> Dict[str, list]:
    """
    Get supported codec information from FFmpeg.
    
    Returns:
        Dictionary with codec information
    """
    codecs = {'audio': [], 'video': []}
    
    try:
        # Get audio codecs
        result = subprocess.run(['ffmpeg', '-codecs'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'A' in line[:3] and 'audio' in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        codecs['audio'].append(parts[1])
        
        # Get video codecs
        result = subprocess.run(['ffmpeg', '-codecs'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'V' in line[:3] and 'video' in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        codecs['video'].append(parts[1])
                        
    except Exception as e:
        logging.error(f"Error getting codec info: {e}")
    
    return codecs


def estimate_conversion_time(input_file: str, target_format: str) -> Optional[int]:
    """
    Estimate conversion time based on file size and format.
    
    Args:
        input_file: Path to input file
        target_format: Target format
        
    Returns:
        Estimated time in seconds or None if cannot estimate
    """
    try:
        file_size = Path(input_file).stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        # Rough estimates based on file size and format
        if target_format in ['mp3', 'wav', 'flac', 'aac', 'ogg']:
            # Audio conversion: ~1 second per MB
            return int(file_size_mb)
        elif target_format in ['mp4', 'avi', 'mov', 'webm']:
            # Video conversion: ~3 seconds per MB
            return int(file_size_mb * 3)
        elif target_format in ['jpg', 'png', 'webp']:
            # Image conversion: ~0.5 seconds per MB
            return int(file_size_mb * 0.5)
        else:
            return None
            
    except Exception:
        return None

