"""
Base converter class for media conversion operations.
"""

import os
import subprocess
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from pathlib import Path


class BaseConverter(ABC):
    """Base class for all media converters."""
    
    def __init__(self, config):
        """
        Initialize the base converter.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def convert(self, input_path: str, output_path: str, 
                target_format: str, quality: str = 'medium', 
                **kwargs) -> Tuple[bool, str]:
        """
        Convert a file to the target format.
        
        Args:
            input_path: Path to input file
            output_path: Path for output file
            target_format: Target format
            quality: Quality preset (low, medium, high)
            **kwargs: Additional conversion parameters
            
        Returns:
            Tuple of (success, error_message)
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> list:
        """
        Get list of supported output formats.
        
        Returns:
            List of supported format strings
        """
        pass
    
    def validate_input_file(self, input_path: str) -> Tuple[bool, str]:
        """
        Validate input file exists and is accessible.
        
        Args:
            input_path: Path to input file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not os.path.exists(input_path):
            return False, f"Input file not found: {input_path}"
        
        if not os.path.isfile(input_path):
            return False, f"Input path is not a file: {input_path}"
        
        if not os.access(input_path, os.R_OK):
            return False, f"Cannot read input file: {input_path}"
        
        return True, ""
    
    def validate_output_path(self, output_path: str) -> Tuple[bool, str]:
        """
        Validate output path is writable.
        
        Args:
            output_path: Path for output file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        output_dir = os.path.dirname(output_path)
        
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                return False, f"Cannot create output directory: {e}"
        
        if os.path.exists(output_path):
            if not os.access(output_path, os.W_OK):
                return False, f"Cannot write to existing output file: {output_path}"
        else:
            try:
                # Test if we can create the file
                with open(output_path, 'w') as f:
                    pass
                os.remove(output_path)
            except Exception as e:
                return False, f"Cannot write to output path: {e}"
        
        return True, ""
    
    def run_ffmpeg_command(self, cmd: list, timeout: int = 300) -> Tuple[bool, str, str]:
        """
        Run an FFmpeg command with proper error handling.
        
        Args:
            cmd: FFmpeg command list
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            self.logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.config.TEMP_FOLDER
            )
            
            if result.returncode == 0:
                self.logger.info("FFmpeg command completed successfully")
                return True, result.stdout, result.stderr
            else:
                self.logger.error(f"FFmpeg command failed: {result.stderr}")
                return False, result.stdout, result.stderr
                
        except subprocess.TimeoutExpired:
            error_msg = f"FFmpeg command timed out after {timeout} seconds"
            self.logger.error(error_msg)
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Error running FFmpeg command: {e}"
            self.logger.error(error_msg)
            return False, "", error_msg
    
    def cleanup_on_error(self, output_path: str) -> None:
        """
        Clean up output file if conversion failed.
        
        Args:
            output_path: Path to output file to remove
        """
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
                self.logger.info(f"Cleaned up failed output file: {output_path}")
        except Exception as e:
            self.logger.warning(f"Could not clean up output file {output_path}: {e}")
    
    def get_file_size_mb(self, file_path: str) -> float:
        """
        Get file size in megabytes.
        
        Args:
            file_path: Path to file
            
        Returns:
            File size in MB
        """
        try:
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
        except Exception:
            return 0.0
    
    def log_conversion_stats(self, input_path: str, output_path: str, 
                           start_time: float, end_time: float) -> None:
        """
        Log conversion statistics.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file
            start_time: Start time timestamp
            end_time: End time timestamp
        """
        try:
            input_size = self.get_file_size_mb(input_path)
            output_size = self.get_file_size_mb(output_path)
            duration = end_time - start_time
            
            compression_ratio = (1 - output_size / input_size) * 100 if input_size > 0 else 0
            
            self.logger.info(
                f"Conversion completed - "
                f"Input: {input_size:.2f}MB, "
                f"Output: {output_size:.2f}MB, "
                f"Duration: {duration:.2f}s, "
                f"Compression: {compression_ratio:.1f}%"
            )
        except Exception as e:
            self.logger.warning(f"Could not log conversion stats: {e}")

