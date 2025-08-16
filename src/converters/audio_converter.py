"""
Audio converter for the Media Converter service.
"""

import os
import time
import logging
from typing import Tuple, Optional
from .base_converter import BaseConverter


class AudioConverter(BaseConverter):
    """Handles audio file conversions using FFmpeg."""
    
    def __init__(self, config):
        """Initialize the audio converter."""
        super().__init__(config)
        self.supported_formats = ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a']
        
    def get_supported_formats(self) -> list:
        """Get list of supported audio output formats."""
        return self.supported_formats
    
    def convert(self, input_path: str, output_path: str, 
                target_format: str, quality: str = 'medium', 
                **kwargs) -> Tuple[bool, str]:
        """
        Convert audio file to target format.
        
        Args:
            input_path: Path to input audio file
            output_path: Path for output audio file
            target_format: Target audio format
            quality: Quality preset (low, medium, high)
            **kwargs: Additional parameters (bitrate, sample_rate, etc.)
            
        Returns:
            Tuple of (success, error_message)
        """
        start_time = time.time()
        
        # Validate inputs
        is_valid, error_msg = self.validate_input_file(input_path)
        if not is_valid:
            return False, error_msg
            
        is_valid, error_msg = self.validate_output_path(output_path)
        if not is_valid:
            return False, error_msg
            
        if target_format not in self.supported_formats:
            return False, f"Unsupported target format: {target_format}"
        
        try:
            # Build FFmpeg command
            cmd = self._build_ffmpeg_command(
                input_path, output_path, target_format, quality, **kwargs
            )
            
            # Run conversion
            success, stdout, stderr = self.run_ffmpeg_command(cmd)
            
            if success:
                # Log conversion stats
                end_time = time.time()
                self.log_conversion_stats(input_path, output_path, start_time, end_time)
                return True, ""
            else:
                # Clean up failed output
                self.cleanup_on_error(output_path)
                return False, f"FFmpeg conversion failed: {stderr}"
                
        except Exception as e:
            self.cleanup_on_error(output_path)
            error_msg = f"Audio conversion error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _build_ffmpeg_command(self, input_path: str, output_path: str, 
                             target_format: str, quality: str, **kwargs) -> list:
        """
        Build FFmpeg command for audio conversion.
        
        Args:
            input_path: Input file path
            output_path: Output file path
            target_format: Target format
            quality: Quality preset
            **kwargs: Additional parameters
            
        Returns:
            FFmpeg command list
        """
        cmd = ['ffmpeg', '-i', input_path, '-y']  # -y overwrites output
        
        # Add quality settings
        bitrate = kwargs.get('bitrate') or self.config.AUDIO_QUALITY_PRESETS.get(quality, '192k')
        sample_rate = kwargs.get('sample_rate', '44100')
        channels = kwargs.get('channels', '2')
        
        # Add audio codec and quality parameters
        if target_format == 'mp3':
            cmd.extend(['-c:a', 'libmp3lame', '-b:a', bitrate])
        elif target_format == 'wav':
            cmd.extend(['-c:a', 'pcm_s16le'])
        elif target_format == 'flac':
            cmd.extend(['-c:a', 'flac'])
        elif target_format == 'aac':
            cmd.extend(['-c:a', 'aac', '-b:a', bitrate])
        elif target_format == 'ogg':
            cmd.extend(['-c:a', 'libvorbis', '-b:a', bitrate])
        elif target_format == 'm4a':
            cmd.extend(['-c:a', 'aac', '-b:a', bitrate])
        
        # Add common audio parameters
        cmd.extend(['-ar', sample_rate, '-ac', channels])
        
        # Add output file
        cmd.append(output_path)
        
        return cmd
    
    def extract_audio_from_video(self, video_path: str, output_path: str, 
                                audio_format: str = 'mp3', quality: str = 'medium') -> Tuple[bool, str]:
        """
        Extract audio from video file.
        
        Args:
            video_path: Path to video file
            output_path: Path for output audio file
            audio_format: Target audio format
            quality: Quality preset
            
        Returns:
            Tuple of (success, error_message)
        """
        if audio_format not in self.supported_formats:
            return False, f"Unsupported audio format: {audio_format}"
        
        # Build FFmpeg command for audio extraction
        cmd = ['ffmpeg', '-i', video_path, '-vn', '-y']  # -vn removes video
        
        # Add audio codec and quality
        bitrate = self.config.AUDIO_QUALITY_PRESETS.get(quality, '192k')
        
        if audio_format == 'mp3':
            cmd.extend(['-c:a', 'libmp3lame', '-b:a', bitrate])
        elif audio_format == 'wav':
            cmd.extend(['-c:a', 'pcm_s16le'])
        elif audio_format == 'flac':
            cmd.extend(['-c:a', 'flac'])
        elif audio_format == 'aac':
            cmd.extend(['-c:a', 'aac', '-b:a', bitrate])
        elif audio_format == 'ogg':
            cmd.extend(['-c:a', 'libvorbis', '-b:a', bitrate])
        elif audio_format == 'm4a':
            cmd.extend(['-c:a', 'aac', '-b:a', bitrate])
        
        cmd.append(output_path)
        
        # Run extraction
        success, stdout, stderr = self.run_ffmpeg_command(cmd)
        
        if success:
            self.logger.info(f"Audio extracted from video: {video_path} -> {output_path}")
            return True, ""
        else:
            self.cleanup_on_error(output_path)
            return False, f"Audio extraction failed: {stderr}"
    
    def get_audio_duration(self, audio_path: str) -> Optional[float]:
        """
        Get duration of audio file in seconds.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds or None if unavailable
        """
        try:
            cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
                   '-of', 'default=noprint_wrappers=1:nokey=1', audio_path]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except Exception as e:
            self.logger.warning(f"Could not get audio duration: {e}")
        
        return None
    
    def normalize_audio(self, input_path: str, output_path: str, 
                       target_format: str = None, target_level: float = -20.0) -> Tuple[bool, str]:
        """
        Normalize audio levels.
        
        Args:
            input_path: Path to input audio file
            output_path: Path for output audio file
            target_format: Target format (uses input format if None)
            target_level: Target loudness level in dB
            
        Returns:
            Tuple of (success, error_message)
        """
        if target_format is None:
            target_format = os.path.splitext(input_path)[1][1:]
        
        if target_format not in self.supported_formats:
            return False, f"Unsupported target format: {target_format}"
        
        # Build normalization command
        cmd = ['ffmpeg', '-i', input_path, '-y']
        
        # Add audio normalization filter
        cmd.extend(['-af', f'loudnorm=I={target_level}:TP=-1.5:LRA=11'])
        
        # Add codec settings
        bitrate = self.config.AUDIO_QUALITY_PRESETS.get('medium', '192k')
        
        if target_format == 'mp3':
            cmd.extend(['-c:a', 'libmp3lame', '-b:a', bitrate])
        elif target_format == 'wav':
            cmd.extend(['-c:a', 'pcm_s16le'])
        elif target_format == 'flac':
            cmd.extend(['-c:a', 'flac'])
        elif target_format == 'aac':
            cmd.extend(['-c:a', 'aac', '-b:a', bitrate])
        elif target_format == 'ogg':
            cmd.extend(['-c:a', 'libvorbis', '-b:a', bitrate])
        elif target_format == 'm4a':
            cmd.extend(['-c:a', 'aac', '-b:a', bitrate])
        
        cmd.append(output_path)
        
        # Run normalization
        success, stdout, stderr = self.run_ffmpeg_command(cmd)
        
        if success:
            self.logger.info(f"Audio normalized: {input_path} -> {output_path}")
            return True, ""
        else:
            self.cleanup_on_error(output_path)
            return False, f"Audio normalization failed: {stderr}"

