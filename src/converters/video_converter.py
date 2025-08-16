"""
Video converter for the Media Converter service.
"""

import os
import time
import logging
from typing import Tuple, Optional
from .base_converter import BaseConverter


class VideoConverter(BaseConverter):
    """Handles video file conversions using FFmpeg."""
    
    def __init__(self, config):
        """Initialize the video converter."""
        super().__init__(config)
        self.supported_formats = ['mp4', 'avi', 'mov', 'webm', 'mkv']
        
    def get_supported_formats(self) -> list:
        """Get list of supported video output formats."""
        return self.supported_formats
    
    def convert(self, input_path: str, output_path: str, 
                target_format: str, quality: str = 'medium', 
                **kwargs) -> Tuple[bool, str]:
        """
        Convert video file to target format.
        
        Args:
            input_path: Path to input video file
            output_path: Path for output video file
            target_format: Target video format
            quality: Quality preset (low, medium, high)
            **kwargs: Additional parameters (resolution, fps, etc.)
            
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
            error_msg = f"Video conversion error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _build_ffmpeg_command(self, input_path: str, output_path: str, 
                             target_format: str, quality: str, **kwargs) -> list:
        """
        Build FFmpeg command for video conversion.
        
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
        crf = kwargs.get('crf') or self.config.VIDEO_QUALITY_PRESETS.get(quality, '20')
        resolution = kwargs.get('resolution')
        fps = kwargs.get('fps')
        
        # Add video codec
        if target_format == 'mp4':
            cmd.extend(['-c:v', 'libx264', '-preset', 'medium'])
        elif target_format == 'avi':
            cmd.extend(['-c:v', 'libx264', '-preset', 'medium'])
        elif target_format == 'mov':
            cmd.extend(['-c:v', 'libx264', '-preset', 'medium'])
        elif target_format == 'webm':
            cmd.extend(['-c:v', 'libvpx-vp9', '-crf', '30'])
        elif target_format == 'mkv':
            cmd.extend(['-c:v', 'libx264', '-preset', 'medium'])
        
        # Add quality parameter (CRF for H.264, different for VP9)
        if target_format in ['mp4', 'avi', 'mov', 'mkv']:
            cmd.extend(['-crf', str(crf)])
        
        # Add resolution if specified
        if resolution:
            cmd.extend(['-vf', f'scale={resolution}'])
        
        # Add FPS if specified
        if fps:
            cmd.extend(['-r', str(fps)])
        
        # Add audio codec (copy if possible, otherwise transcode)
        audio_codec = kwargs.get('audio_codec', 'copy')
        if audio_codec != 'copy':
            cmd.extend(['-c:a', audio_codec])
        else:
            cmd.extend(['-c:a', 'copy'])
        
        # Add output file
        cmd.append(output_path)
        
        return cmd
    
    def extract_frames(self, video_path: str, output_dir: str, 
                      fps: int = 1, format: str = 'jpg') -> Tuple[bool, str]:
        """
        Extract frames from video file.
        
        Args:
            video_path: Path to video file
            output_dir: Directory for output frames
            fps: Frames per second to extract
            format: Output image format
            
        Returns:
            Tuple of (success, error_message)
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        output_pattern = os.path.join(output_dir, f"frame_%04d.{format}")
        
        cmd = [
            'ffmpeg', '-i', video_path, '-vf', f'fps={fps}',
            '-y', output_pattern
        ]
        
        success, stdout, stderr = self.run_ffmpeg_command(cmd)
        
        if success:
            self.logger.info(f"Frames extracted from video: {video_path} -> {output_dir}")
            return True, ""
        else:
            return False, f"Frame extraction failed: {stderr}"
    
    def create_thumbnail(self, video_path: str, output_path: str, 
                        time_position: str = '00:00:01', 
                        size: str = '320x240') -> Tuple[bool, str]:
        """
        Create thumbnail from video file.
        
        Args:
            video_path: Path to video file
            output_path: Path for output thumbnail
            time_position: Time position for thumbnail (HH:MM:SS)
            size: Thumbnail size (WxH)
            
        Returns:
            Tuple of (success, error_message)
        """
        cmd = [
            'ffmpeg', '-i', video_path, '-ss', time_position,
            '-vframes', '1', '-vf', f'scale={size}',
            '-y', output_path
        ]
        
        success, stdout, stderr = self.run_ffmpeg_command(cmd)
        
        if success:
            self.logger.info(f"Thumbnail created: {video_path} -> {output_path}")
            return True, ""
        else:
            self.cleanup_on_error(output_path)
            return False, f"Thumbnail creation failed: {stderr}"
    
    def get_video_info(self, video_path: str) -> Optional[dict]:
        """
        Get detailed video information.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information or None
        """
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                import json
                probe = json.loads(result.stdout)
                
                info = {
                    'duration': float(probe['format']['duration']) if 'duration' in probe['format'] else None,
                    'size': int(probe['format']['size']) if 'size' in probe['format'] else None,
                    'bitrate': int(probe['format']['bit_rate']) if 'bit_rate' in probe['format'] else None
                }
                
                # Get video stream info
                video_stream = next((stream for stream in probe['streams'] 
                                   if stream['codec_type'] == 'video'), None)
                if video_stream:
                    info.update({
                        'width': int(video_stream.get('width', 0)),
                        'height': int(video_stream.get('height', 0)),
                        'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                        'codec': video_stream.get('codec_name', 'unknown')
                    })
                
                # Get audio stream info
                audio_stream = next((stream for stream in probe['streams'] 
                                   if stream['codec_type'] == 'audio'), None)
                if audio_stream:
                    info.update({
                        'audio_codec': audio_stream.get('codec_name', 'unknown'),
                        'audio_channels': int(audio_stream.get('channels', 0)),
                        'audio_sample_rate': int(audio_stream.get('sample_rate', 0))
                    })
                
                return info
                
        except Exception as e:
            self.logger.warning(f"Could not get video info: {e}")
        
        return None
    
    def compress_video(self, input_path: str, output_path: str, 
                      target_size_mb: float, quality: str = 'medium') -> Tuple[bool, str]:
        """
        Compress video to target file size.
        
        Args:
            input_path: Path to input video file
            output_path: Path for output video file
            target_size_mb: Target file size in MB
            quality: Quality preset
            
        Returns:
            Tuple of (success, error_message)
        """
        # Get input video info
        video_info = self.get_video_info(input_path)
        if not video_info:
            return False, "Could not get video information"
        
        # Calculate target bitrate
        duration = video_info.get('duration', 0)
        if duration <= 0:
            return False, "Invalid video duration"
        
        target_size_bits = target_size_mb * 8 * 1024 * 1024
        target_bitrate = int(target_size_bits / duration)
        
        # Build compression command
        cmd = ['ffmpeg', '-i', input_path, '-y']
        
        # Add video codec with target bitrate
        cmd.extend(['-c:v', 'libx264', '-preset', 'medium', '-b:v', str(target_bitrate)])
        
        # Add audio codec
        cmd.extend(['-c:a', 'aac', '-b:a', '128k'])
        
        # Add output file
        cmd.append(output_path)
        
        # Run compression
        success, stdout, stderr = self.run_ffmpeg_command(cmd)
        
        if success:
            self.logger.info(f"Video compressed: {input_path} -> {output_path}")
            return True, ""
        else:
            self.cleanup_on_error(output_path)
            return False, f"Video compression failed: {stderr}"

