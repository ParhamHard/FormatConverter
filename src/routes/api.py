"""
API routes for the Media Converter service.
"""

import os
import uuid
import time
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from ..converters import AudioConverter, VideoConverter, ImageConverter
from ..utils.file_utils import allowed_file, get_file_info, generate_unique_filename, cleanup_temp_files
from ..utils.ffmpeg_utils import check_ffmpeg_available

# Create blueprint
api_bp = Blueprint('api', __name__)


@api_bp.route('/convert', methods=['POST'])
def convert_file():
    """
    Convert uploaded file to target format.
    
    Expected form data:
    - file: File to convert
    - target_format: Desired output format
    - quality: Quality preset (low, medium, high) - optional
    - extract_audio: Whether to extract audio from video - optional
    
    Returns:
        JSON response with conversion status and download URL
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Get conversion parameters
        target_format = request.form.get('target_format')
        if not target_format:
            return jsonify({
                'success': False,
                'error': 'Target format not specified'
            }), 400
        
        quality = request.form.get('quality', 'medium')
        extract_audio = request.form.get('extract_audio', 'false').lower() == 'true'
        
        # Validate file
        if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Supported: {", ".join(current_app.config["ALLOWED_EXTENSIONS"])}'
            }), 400
        
        # Check FFmpeg availability
        is_available, error_msg = check_ffmpeg_available()
        if not is_available:
            return jsonify({
                'success': False,
                'error': f'FFmpeg not available: {error_msg}'
            }), 500
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(upload_path)
        
        try:
            # Get file info
            file_info = get_file_info(upload_path)
            file_type = file_info.get('type', 'unknown')
            
            # Generate output filename
            output_filename = generate_unique_filename(filename, target_format)
            output_path = os.path.join(current_app.config['CONVERTED_FOLDER'], output_filename)
            
            # Perform conversion based on file type
            success = False
            error_message = ""
            
            if file_type == 'audio' or (file_type == 'video' and extract_audio):
                # Audio conversion or audio extraction from video
                converter = AudioConverter(current_app.config)
                
                if extract_audio and file_type == 'video':
                    success, error_message = converter.extract_audio_from_video(
                        upload_path, output_path, target_format, quality
                    )
                else:
                    success, error_message = converter.convert(
                        upload_path, output_path, target_format, quality
                    )
                    
            elif file_type == 'video':
                # Video conversion
                converter = VideoConverter(current_app.config)
                success, error_message = converter.convert(
                    upload_path, output_path, target_format, quality
                )
                
            elif file_type == 'image':
                # Image conversion
                converter = ImageConverter(current_app.config)
                success, error_message = converter.convert(
                    upload_path, output_path, target_format, quality
                )
                
            else:
                error_message = f"Unsupported file type: {file_type}"
            
            # Clean up uploaded file
            cleanup_temp_files(upload_path)
            
            if success:
                # Get output file info
                output_info = get_file_info(output_path)
                
                return jsonify({
                    'success': True,
                    'message': 'File converted successfully',
                    'download_url': f'/api/download/{output_filename}',
                    'filename': output_filename,
                    'original_size': file_info.get('size', 0),
                    'converted_size': output_info.get('size', 0),
                    'format': target_format,
                    'quality': quality
                })
            else:
                # Clean up failed output
                cleanup_temp_files(output_path)
                return jsonify({
                    'success': False,
                    'error': f'Conversion failed: {error_message}'
                }), 500
                
        except Exception as e:
            # Clean up uploaded file on error
            cleanup_temp_files(upload_path)
            current_app.logger.error(f"Conversion error: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Conversion error: {str(e)}'
            }), 500
            
    except RequestEntityTooLarge:
        return jsonify({
            'success': False,
            'error': 'File too large'
        }), 413
    except Exception as e:
        current_app.logger.error(f"Unexpected error in convert_file: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@api_bp.route('/download/<filename>')
def download_file(filename):
    """
    Download converted file.
    
    Args:
        filename: Name of the file to download
        
    Returns:
        File download response
    """
    try:
        file_path = os.path.join(current_app.config['CONVERTED_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        current_app.logger.error(f"Download error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Download failed'
        }), 500


@api_bp.route('/formats')
def get_supported_formats():
    """
    Get list of supported input and output formats.
    
    Returns:
        JSON response with supported formats
    """
    try:
        # Check FFmpeg availability
        is_available, error_msg = check_ffmpeg_available()
        
        if not is_available:
            return jsonify({
                'success': False,
                'error': f'FFmpeg not available: {error_msg}',
                'formats': {}
            }), 500
        
        # Get formats from converters
        audio_converter = AudioConverter(current_app.config)
        video_converter = VideoConverter(current_app.config)
        image_converter = ImageConverter(current_app.config)
        
        formats = {
            'audio': {
                'input': ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'],
                'output': audio_converter.get_supported_formats()
            },
            'video': {
                'input': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm'],
                'output': video_converter.get_supported_formats()
            },
            'image': {
                'input': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'],
                'output': image_converter.get_supported_formats()
            }
        }
        
        return jsonify({
            'success': True,
            'formats': formats,
            'ffmpeg_available': is_available
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting formats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get supported formats'
        }), 500


@api_bp.route('/health')
def health_check():
    """
    Health check endpoint for the API.
    
    Returns:
        JSON response with API health status
    """
    try:
        # Check FFmpeg availability
        is_available, error_msg = check_ffmpeg_available()
        
        # Check directory permissions
        upload_writable = os.access(current_app.config['UPLOAD_FOLDER'], os.W_OK)
        converted_writable = os.access(current_app.config['CONVERTED_FOLDER'], os.W_OK)
        
        health_status = {
            'status': 'healthy' if is_available and upload_writable and converted_writable else 'degraded',
            'timestamp': datetime.utcnow().isoformat(),
            'ffmpeg': {
                'available': is_available,
                'error': error_msg if not is_available else None
            },
            'directories': {
                'uploads': {
                    'path': current_app.config['UPLOAD_FOLDER'],
                    'writable': upload_writable
                },
                'converted': {
                    'path': current_app.config['CONVERTED_FOLDER'],
                    'writable': converted_writable
                }
            },
            'config': {
                'max_file_size': current_app.config['MAX_FILE_SIZE'],
                'allowed_extensions': current_app.config['ALLOWED_EXTENSIONS']
            }
        }
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        return jsonify(health_status), status_code
        
    except Exception as e:
        current_app.logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@api_bp.route('/info/<filename>')
def get_file_info_endpoint(filename):
    """
    Get information about a file.
    
    Args:
        filename: Name of the file to get info for
        
    Returns:
        JSON response with file information
    """
    try:
        # Check if file exists in uploads or converted
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        converted_path = os.path.join(current_app.config['CONVERTED_FOLDER'], filename)
        
        if os.path.exists(upload_path):
            file_path = upload_path
        elif os.path.exists(converted_path):
            file_path = converted_path
        else:
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        # Get file info
        file_info = get_file_info(file_path)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'info': file_info
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting file info: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get file information'
        }), 500

