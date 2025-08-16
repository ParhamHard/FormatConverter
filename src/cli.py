"""
Command Line Interface for the Media Converter service.
"""

import click
import os
import sys
from pathlib import Path

from .config import get_config
from .converters import AudioConverter, VideoConverter, ImageConverter
from .utils.ffmpeg_utils import check_ffmpeg_available


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Universal Media Converter - Command Line Interface."""
    pass


@cli.command()
@click.option('--config', '-c', default=None, help='Configuration name to use')
def check(config):
    """Check system requirements and configuration."""
    click.echo("🔍 Checking system requirements...")
    
    # Check FFmpeg
    is_available, error_msg = check_ffmpeg_available()
    if is_available:
        click.echo("✅ FFmpeg is available")
    else:
        click.echo(f"❌ FFmpeg not available: {error_msg}")
        sys.exit(1)
    
    # Load configuration
    try:
        config_obj = get_config(config)
        click.echo(f"✅ Configuration loaded: {config.__class__.__name__}")
        
        # Check directories
        for dir_name, dir_path in [
            ('Uploads', config_obj.UPLOAD_FOLDER),
            ('Converted', config_obj.CONVERTED_FOLDER),
            ('Temp', config_obj.TEMP_FOLDER)
        ]:
            if os.access(dir_path, os.W_OK):
                click.echo(f"✅ {dir_name} directory: {dir_path}")
            else:
                click.echo(f"❌ {dir_name} directory not writable: {dir_path}")
                
    except Exception as e:
        click.echo(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    click.echo("🎉 System check completed successfully!")


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--format', '-f', required=True, help='Target format')
@click.option('--quality', '-q', default='medium', type=click.Choice(['low', 'medium', 'high']), help='Quality preset')
@click.option('--config', '-c', default=None, help='Configuration name to use')
def convert(input_file, output_file, format, quality, config):
    """Convert a file to the target format."""
    click.echo(f"🔄 Converting {input_file} to {format}...")
    
    # Load configuration
    try:
        config_obj = get_config(config)
    except Exception as e:
        click.echo(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Check FFmpeg
    is_available, error_msg = check_ffmpeg_available()
    if not is_available:
        click.echo(f"❌ FFmpeg not available: {error_msg}")
        sys.exit(1)
    
    # Determine file type and converter
    input_path = Path(input_file)
    file_extension = input_path.suffix.lower()
    
    if file_extension in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']:
        converter = AudioConverter(config_obj)
        file_type = 'audio'
    elif file_extension in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']:
        converter = VideoConverter(config_obj)
        file_type = 'video'
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
        converter = ImageConverter(config_obj)
        file_type = 'image'
    else:
        click.echo(f"❌ Unsupported file type: {file_extension}")
        sys.exit(1)
    
    click.echo(f"📁 File type: {file_type}")
    click.echo(f"🎯 Target format: {format}")
    click.echo(f"⭐ Quality: {quality}")
    
    # Perform conversion
    try:
        success, error_message = converter.convert(
            str(input_file), str(output_file), format, quality
        )
        
        if success:
            click.echo(f"✅ Conversion completed successfully!")
            click.echo(f"📁 Output: {output_file}")
            
            # Show file sizes
            input_size = os.path.getsize(input_file) / (1024 * 1024)
            output_size = os.path.getsize(output_file) / (1024 * 1024)
            compression = (1 - output_size / input_size) * 100
            
            click.echo(f"📊 Input size: {input_size:.2f} MB")
            click.echo(f"📊 Output size: {output_size:.2f} MB")
            click.echo(f"📊 Compression: {compression:.1f}%")
            
        else:
            click.echo(f"❌ Conversion failed: {error_message}")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Conversion error: {e}")
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--format', '-f', default='mp3', help='Audio format for extraction')
@click.option('--quality', '-q', default='medium', type=click.Choice(['low', 'medium', 'high']), help='Quality preset')
@click.option('--config', '-c', default=None, help='Configuration name to use')
def extract_audio(input_file, output_file, format, quality, config):
    """Extract audio from video file."""
    click.echo(f"🎵 Extracting audio from {input_file}...")
    
    # Load configuration
    try:
        config_obj = get_config(config)
    except Exception as e:
        click.echo(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Check FFmpeg
    is_available, error_msg = check_ffmpeg_available()
    if not is_available:
        click.echo(f"❌ FFmpeg not available: {error_msg}")
        sys.exit(1)
    
    # Check if input is video
    input_path = Path(input_file)
    file_extension = input_path.suffix.lower()
    
    if file_extension not in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']:
        click.echo(f"❌ Input file is not a video: {file_extension}")
        sys.exit(1)
    
    # Extract audio
    try:
        converter = AudioConverter(config_obj)
        success, error_message = converter.extract_audio_from_video(
            str(input_file), str(output_file), format, quality
        )
        
        if success:
            click.echo(f"✅ Audio extraction completed successfully!")
            click.echo(f"🎵 Output: {output_file}")
            
            # Show file sizes
            input_size = os.path.getsize(input_file) / (1024 * 1024)
            output_size = os.path.getsize(output_file) / (1024 * 1024)
            
            click.echo(f"📊 Video size: {input_size:.2f} MB")
            click.echo(f"📊 Audio size: {output_size:.2f} MB")
            
        else:
            click.echo(f"❌ Audio extraction failed: {error_message}")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Audio extraction error: {e}")
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--width', '-w', type=int, help='Target width')
@click.option('--height', '-h', type=int, help='Target height')
@click.option('--maintain-aspect', is_flag=True, default=True, help='Maintain aspect ratio')
@click.option('--format', '-f', help='Target format (uses input format if not specified)')
@click.option('--config', '-c', default=None, help='Configuration name to use')
def resize(input_file, output_file, width, height, maintain_aspect, format, config):
    """Resize image to specified dimensions."""
    if not width and not height:
        click.echo("❌ Please specify at least width or height")
        sys.exit(1)
    
    click.echo(f"🖼️  Resizing {input_file}...")
    
    # Load configuration
    try:
        config_obj = get_config(config)
    except Exception as e:
        click.echo(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Check FFmpeg
    is_available, error_msg = check_ffmpeg_available()
    if not is_available:
        click.echo(f"❌ FFmpeg not available: {error_msg}")
        sys.exit(1)
    
    # Check if input is image
    input_path = Path(input_file)
    file_extension = input_path.suffix.lower()
    
    if file_extension not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
        click.echo(f"❌ Input file is not an image: {file_extension}")
        sys.exit(1)
    
    # Resize image
    try:
        converter = ImageConverter(config_obj)
        success, error_message = converter.resize_image(
            str(input_file), str(output_file), width, height, maintain_aspect, format
        )
        
        if success:
            click.echo(f"✅ Image resize completed successfully!")
            click.echo(f"🖼️  Output: {output_file}")
            
            # Show dimensions
            if width and height:
                click.echo(f"📐 Dimensions: {width}x{height}")
            elif width:
                click.echo(f"📐 Width: {width} (height auto-scaled)")
            else:
                click.echo(f"📐 Height: {height} (width auto-scaled)")
                
        else:
            click.echo(f"❌ Image resize failed: {error_message}")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Image resize error: {e}")
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--config', '-c', default=None, help='Configuration name to use')
def info(input_file, config):
    """Get detailed information about a file."""
    click.echo(f"ℹ️  Getting information for {input_file}...")
    
    # Load configuration
    try:
        config_obj = get_config(config)
    except Exception as e:
        click.echo(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Check FFmpeg
    is_available, error_msg = check_ffmpeg_available()
    if not is_available:
        click.echo(f"❌ FFmpeg not available: {error_msg}")
        sys.exit(1)
    
    # Get file info
    try:
        from .utils.file_utils import get_file_info
        
        file_info = get_file_info(input_file)
        
        click.echo(f"📁 File: {input_file}")
        click.echo(f"📊 Size: {file_info.get('size', 0) / (1024 * 1024):.2f} MB")
        click.echo(f"🎭 Type: {file_info.get('type', 'unknown')}")
        
        if file_info.get('type') == 'audio':
            duration = file_info.get('duration')
            if duration:
                click.echo(f"⏱️  Duration: {duration:.2f} seconds")
                
        elif file_info.get('type') == 'video':
            duration = file_info.get('duration')
            width = file_info.get('width')
            height = file_info.get('height')
            
            if duration:
                click.echo(f"⏱️  Duration: {duration:.2f} seconds")
            if width and height:
                click.echo(f"📐 Resolution: {width}x{height}")
                
        elif file_info.get('type') == 'image':
            width = file_info.get('width')
            height = file_info.get('height')
            
            if width and height:
                click.echo(f"📐 Dimensions: {width}x{height}")
                
    except Exception as e:
        click.echo(f"❌ Error getting file info: {e}")
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', default=None, help='Configuration name to use')
def formats(config):
    """Show supported input and output formats."""
    click.echo("📋 Supported formats:")
    
    # Load configuration
    try:
        config_obj = get_config(config)
    except Exception as e:
        click.echo(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Get converters
    audio_converter = AudioConverter(config_obj)
    video_converter = VideoConverter(config_obj)
    image_converter = ImageConverter(config_obj)
    
    click.echo("\n🎵 Audio:")
    click.echo(f"  Input:  {', '.join(['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'])}")
    click.echo(f"  Output: {', '.join(audio_converter.get_supported_formats())}")
    
    click.echo("\n🎬 Video:")
    click.echo(f"  Input:  {', '.join(['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm'])}")
    click.echo(f"  Output: {', '.join(video_converter.get_supported_formats())}")
    
    click.echo("\n🖼️  Image:")
    click.echo(f"  Input:  {', '.join(['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'])}")
    click.echo(f"  Output: {', '.join(image_converter.get_supported_formats())}")


if __name__ == '__main__':
    cli()

