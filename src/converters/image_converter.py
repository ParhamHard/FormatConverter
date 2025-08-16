"""
Image converter for the Media Converter service.
"""

import os
import time
import logging
from typing import Tuple, Optional
from .base_converter import BaseConverter


class ImageConverter(BaseConverter):
    """Handles image file conversions using FFmpeg."""
    
    def __init__(self, config):
        """Initialize the image converter."""
        super().__init__(config)
        self.supported_formats = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp']
        
    def get_supported_formats(self) -> list:
        """Get list of supported image output formats."""
        return self.supported_formats
    
    def convert(self, input_path: str, output_path: str, 
                target_format: str, quality: str = 'medium', 
                **kwargs) -> Tuple[bool, str]:
        """
        Convert image file to target format.
        
        Args:
            input_path: Path to input image file
            output_path: Path for output image file
            target_format: Target image format
            quality: Quality preset (low, medium, high)
            **kwargs: Additional parameters (resolution, compression, etc.)
            
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
            error_msg = f"Image conversion error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _build_ffmpeg_command(self, input_path: str, output_path: str, 
                             target_format: str, quality: str, **kwargs) -> list:
        """
        Build FFmpeg command for image conversion.
        
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
        qscale = kwargs.get('qscale') or self._get_quality_qscale(quality, target_format)
        resolution = kwargs.get('resolution')
        
        # Add quality parameter
        if target_format in ['jpg', 'jpeg']:
            cmd.extend(['-q:v', str(qscale)])
        elif target_format == 'webp':
            cmd.extend(['-quality', str(qscale)])
        elif target_format == 'png':
            # PNG is lossless, no quality setting needed
            pass
        
        # Add resolution if specified
        if resolution:
            cmd.append('-vf')
            if isinstance(resolution, tuple):
                width, height = resolution
                cmd.append(f'scale={width}:{height}')
            else:
                cmd.append(f'scale={resolution}')
        
        # Add output file
        cmd.append(output_path)
        
        return cmd
    
    def _get_quality_qscale(self, quality: str, format: str) -> int:
        """
        Get quality qscale value based on quality preset and format.
        
        Args:
            quality: Quality preset (low, medium, high)
            format: Target format
            
        Returns:
            Quality qscale value
        """
        if format in ['jpg', 'jpeg']:
            # JPEG: lower values = higher quality (2-31)
            quality_map = {'low': 25, 'medium': 15, 'high': 5}
        elif format == 'webp':
            # WebP: higher values = higher quality (0-100)
            quality_map = {'low': 30, 'medium': 60, 'high': 90}
        else:
            # Default quality
            quality_map = {'low': 20, 'medium': 10, 'high': 5}
        
        return quality_map.get(quality, quality_map['medium'])
    
    def resize_image(self, input_path: str, output_path: str, 
                    width: int, height: int, 
                    maintain_aspect: bool = True, 
                    target_format: str = None) -> Tuple[bool, str]:
        """
        Resize image to specified dimensions.
        
        Args:
            input_path: Path to input image file
            output_path: Path for output image file
            width: Target width
            height: Target height
            maintain_aspect: Whether to maintain aspect ratio
            target_format: Target format (uses input format if None)
            
        Returns:
            Tuple of (success, error_message)
        """
        if target_format is None:
            target_format = os.path.splitext(input_path)[1][1:]
        
        if target_format not in self.supported_formats:
            return False, f"Unsupported target format: {target_format}"
        
        # Build resize command
        cmd = ['ffmpeg', '-i', input_path, '-y']
        
        # Add resize filter
        if maintain_aspect:
            cmd.extend(['-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease'])
        else:
            cmd.extend(['-vf', f'scale={width}:{height}'])
        
        # Add quality settings
        qscale = self._get_quality_qscale('medium', target_format)
        if target_format in ['jpg', 'jpeg']:
            cmd.extend(['-q:v', str(qscale)])
        elif target_format == 'webp':
            cmd.extend(['-quality', str(qscale)])
        
        # Add output file
        cmd.append(output_path)
        
        # Run resize
        success, stdout, stderr = self.run_ffmpeg_command(cmd)
        
        if success:
            self.logger.info(f"Image resized: {input_path} -> {output_path}")
            return True, ""
        else:
            self.cleanup_on_error(output_path)
            return False, f"Image resize failed: {stderr}"
    
    def compress_image(self, input_path: str, output_path: str, 
                      target_size_kb: float, 
                      target_format: str = None) -> Tuple[bool, str]:
        """
        Compress image to target file size.
        
        Args:
            input_path: Path to input image file
            output_path: Path for output image file
            target_size_kb: Target file size in KB
            target_format: Target format (uses input format if None)
            
        Returns:
            Tuple of (success, error_message)
        """
        if target_format is None:
            target_format = os.path.splitext(input_path)[1][1:]
        
        if target_format not in self.supported_formats:
            return False, f"Unsupported target format: {target_format}"
        
        # Build compression command
        cmd = ['ffmpeg', '-i', input_path, '-y']
        
        # Add compression settings
        if target_format in ['jpg', 'jpeg']:
            # Start with high quality and reduce until target size is reached
            qscale = 5
            cmd.extend(['-q:v', str(qscale)])
        elif target_format == 'webp':
            quality = 90
            cmd.extend(['-quality', str(quality)])
        elif target_format == 'png':
            # PNG is lossless, use different approach
            cmd.extend(['-compression_level', '9'])
        
        # Add output file
        cmd.append(output_path)
        
        # Run compression
        success, stdout, stderr = self.run_ffmpeg_command(cmd)
        
        if success:
            # Check if target size is met
            output_size_kb = os.path.getsize(output_path) / 1024
            if output_size_kb <= target_size_kb:
                self.logger.info(f"Image compressed: {input_path} -> {output_path}")
                return True, ""
            else:
                # Try with lower quality
                return self._compress_with_lower_quality(
                    input_path, output_path, target_format, target_size_kb
                )
        else:
            self.cleanup_on_error(output_path)
            return False, f"Image compression failed: {stderr}"
    
    def _compress_with_lower_quality(self, input_path: str, output_path: str, 
                                   target_format: str, target_size_kb: float) -> Tuple[bool, str]:
        """
        Compress image with progressively lower quality until target size is met.
        
        Args:
            input_path: Path to input image file
            output_path: Path for output image file
            target_format: Target format
            target_size_kb: Target file size in KB
            
        Returns:
            Tuple of (success, error_message)
        """
        if target_format in ['jpg', 'jpeg']:
            # Try different qscale values
            for qscale in [10, 15, 20, 25, 30]:
                cmd = ['ffmpeg', '-i', input_path, '-y', '-q:v', str(qscale), output_path]
                
                success, stdout, stderr = self.run_ffmpeg_command(cmd)
                if success:
                    output_size_kb = os.path.getsize(output_path) / 1024
                    if output_size_kb <= target_size_kb:
                        self.logger.info(f"Image compressed with qscale {qscale}: {input_path} -> {output_path}")
                        return True, ""
                    else:
                        # Clean up and try next quality level
                        self.cleanup_on_error(output_path)
        
        elif target_format == 'webp':
            # Try different quality values
            for quality in [80, 70, 60, 50, 40, 30]:
                cmd = ['ffmpeg', '-i', input_path, '-y', '-quality', str(quality), output_path]
                
                success, stdout, stderr = self.run_ffmpeg_command(cmd)
                if success:
                    output_size_kb = os.path.getsize(output_path) / 1024
                    if output_size_kb <= target_size_kb:
                        self.logger.info(f"Image compressed with quality {quality}: {input_path} -> {output_path}")
                        return True, ""
                    else:
                        # Clean up and try next quality level
                        self.cleanup_on_error(output_path)
        
        return False, f"Could not compress image to target size: {target_size_kb}KB"
    
    def create_thumbnail(self, input_path: str, output_path: str, 
                        size: str = '150x150', 
                        target_format: str = None) -> Tuple[bool, str]:
        """
        Create thumbnail from image file.
        
        Args:
            input_path: Path to input image file
            output_path: Path for output thumbnail
            size: Thumbnail size (WxH)
            target_format: Target format (uses input format if None)
            
        Returns:
            Tuple of (success, error_message)
        """
        if target_format is None:
            target_format = os.path.splitext(input_path)[1][1:]
        
        if target_format not in self.supported_formats:
            return False, f"Unsupported target format: {target_format}"
        
        # Build thumbnail command
        cmd = ['ffmpeg', '-i', input_path, '-y']
        
        # Add resize filter for thumbnail
        cmd.extend(['-vf', f'scale={size}:force_original_aspect_ratio=decrease,pad={size}:(ow-iw)/2:(oh-ih)/2:white'])
        
        # Add quality settings
        qscale = self._get_quality_qscale('medium', target_format)
        if target_format in ['jpg', 'jpeg']:
            cmd.extend(['-q:v', str(qscale)])
        elif target_format == 'webp':
            cmd.extend(['-quality', str(qscale)])
        
        # Add output file
        cmd.append(output_path)
        
        # Run thumbnail creation
        success, stdout, stderr = self.run_ffmpeg_command(cmd)
        
        if success:
            self.logger.info(f"Thumbnail created: {input_path} -> {output_path}")
            return True, ""
        else:
            self.cleanup_on_error(output_path)
            return False, f"Thumbnail creation failed: {stderr}"
    
    def get_image_info(self, image_path: str) -> Optional[dict]:
        """
        Get detailed image information.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with image information or None
        """
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', image_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                import json
                probe = json.loads(result.stdout)
                
                info = {
                    'size': int(probe['format']['size']) if 'size' in probe['format'] else None,
                    'bitrate': int(probe['format']['bit_rate']) if 'bit_rate' in probe['format'] else None
                }
                
                # Get image stream info
                image_stream = next((stream for stream in probe['streams'] 
                                   if stream['codec_type'] == 'video'), None)
                if image_stream:
                    info.update({
                        'width': int(image_stream.get('width', 0)),
                        'height': int(image_stream.get('height', 0)),
                        'codec': image_stream.get('codec_name', 'unknown'),
                        'pixel_format': image_stream.get('pix_fmt', 'unknown')
                    })
                
                return info
                
        except Exception as e:
            self.logger.warning(f"Could not get image info: {e}")
        
        return None

