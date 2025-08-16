"""
File utility functions for the Media Converter service.
"""

import os
import uuid
import shutil
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path
import subprocess
import json
from mutagen import File


def allowed_file(filename: str, allowed_extensions: list) -> bool:
    """
    Check if a file has an allowed extension.
    
    Args:
        filename: Name of the file to check
        allowed_extensions: List of allowed file extensions
        
    Returns:
        True if file extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_file_info(filepath: str) -> Dict[str, Any]:
    """
    Get basic file information including type, size, and metadata.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Dictionary containing file information
    """
    try:
        file_info = {
            'size': os.path.getsize(filepath),
            'type': 'unknown'
        }
        
        file_extension = Path(filepath).suffix.lower()
        
        if file_extension in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']:
            file_info.update(_get_audio_info(filepath))
        elif file_extension in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']:
            file_info.update(_get_video_info(filepath))
        elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
            file_info.update(_get_image_info(filepath))
            
        return file_info
        
    except Exception as e:
        return {'type': 'unknown', 'size': 0, 'error': str(e)}


def _get_audio_info(filepath: str) -> Dict[str, Any]:
    """Get audio file information using mutagen."""
    try:
        audio = File(filepath)
        if hasattr(audio, 'info') and audio.info:
            duration = audio.info.length if hasattr(audio.info, 'length') else None
            return {
                'type': 'audio',
                'duration': duration
            }
    except Exception:
        pass
    
    return {'type': 'audio'}


def _get_video_info(filepath: str) -> Dict[str, Any]:
    """Get video file information using ffprobe."""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', 
               '-show_format', '-show_streams', filepath]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            probe = json.loads(result.stdout)
            video_stream = next((stream for stream in probe['streams'] 
                               if stream['codec_type'] == 'video'), None)
            
            info = {'type': 'video'}
            
            if 'duration' in probe['format']:
                info['duration'] = float(probe['format']['duration'])
            
            if video_stream:
                info['width'] = int(video_stream.get('width', 0))
                info['height'] = int(video_stream.get('height', 0))
            
            return info
    except Exception:
        pass
    
    return {'type': 'video'}


def _get_image_info(filepath: str) -> Dict[str, Any]:
    """Get image file information using ffprobe."""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', 
               '-show_format', '-show_streams', filepath]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            probe = json.loads(result.stdout)
            video_stream = next((stream for stream in probe['streams'] 
                               if stream['codec_type'] == 'video'), None)
            
            if video_stream:
                return {
                    'type': 'image',
                    'width': int(video_stream.get('width', 0)),
                    'height': int(video_stream.get('height', 0))
                }
    except Exception:
        pass
    
    return {'type': 'image'}


def generate_unique_filename(original_filename: str, target_format: str) -> str:
    """
    Generate a unique filename for converted files.
    
    Args:
        original_filename: Original filename
        target_format: Target format extension
        
    Returns:
        Unique filename with target format
    """
    name = Path(original_filename).stem
    unique_id = str(uuid.uuid4())[:8]
    return f"{name}_{unique_id}.{target_format}"


def cleanup_temp_files(filepath: str) -> None:
    """
    Clean up temporary files.
    
    Args:
        filepath: Path to the file to remove
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception:
        pass


def cleanup_directory(directory: str, max_age_hours: int = 24) -> None:
    """
    Clean up old files in a directory.
    
    Args:
        directory: Directory to clean
        max_age_hours: Maximum age of files in hours
    """
    try:
        current_time = os.time()
        max_age_seconds = max_age_hours * 3600
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    cleanup_temp_files(filepath)
    except Exception:
        pass

