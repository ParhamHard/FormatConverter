import os
import uuid
import subprocess
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
import ffmpeg
from mutagen import File
import tempfile
import shutil

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_FILE_SIZE', '500MB').replace('MB', '')) * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'
app.config['ALLOWED_EXTENSIONS'] = os.environ.get('ALLOWED_EXTENSIONS', 'mp3,wav,flac,aac,ogg,m4a,mp4,avi,mov,wmv,flv,mkv,webm,jpg,jpeg,png,gif,bmp,tiff,webp').split(',')

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_file_info(filepath):
    """Get basic file information"""
    try:
        if filepath.lower().endswith(('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a')):
            # Audio file - use mutagen for basic info
            try:
                audio = File(filepath)
                if hasattr(audio, 'info') and audio.info:
                    duration = audio.info.length if hasattr(audio.info, 'length') else None
                    return {
                        'type': 'audio',
                        'duration': duration,
                        'size': os.path.getsize(filepath)
                    }
                else:
                    # Fallback to just file extension detection
                    return {
                        'type': 'audio',
                        'size': os.path.getsize(filepath)
                    }
            except:
                # Fallback to just file extension detection
                return {
                    'type': 'audio',
                    'size': os.path.getsize(filepath)
                }
        elif filepath.lower().endswith(('.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm')):
            # Video file - use ffprobe command
            try:
                cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', filepath]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    probe = json.loads(result.stdout)
                    video_info = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                    return {
                        'type': 'video',
                        'duration': float(probe['format']['duration']) if 'duration' in probe['format'] else None,
                        'width': int(video_info['width']) if video_info else None,
                        'height': int(video_info['height']) if video_info else None,
                        'size': os.path.getsize(filepath)
                    }
            except:
                # Fallback to just file extension detection
                return {
                    'type': 'video',
                    'size': os.path.getsize(filepath)
                }
        elif filepath.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')):
            # Image file - use ffprobe command
            try:
                cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', filepath]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    probe = json.loads(result.stdout)
                    video_info = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                    return {
                        'type': 'image',
                        'width': int(video_info['width']) if video_info else None,
                        'height': int(video_info['height']) if video_info else None,
                        'size': os.path.getsize(filepath)
                    }
            except:
                # Fallback to just file extension detection
                return {
                    'type': 'image',
                    'size': os.path.getsize(filepath)
                }
    except Exception as e:
        print(f"Error getting file info: {e}")
    
    return {'type': 'unknown', 'size': os.path.getsize(filepath)}

def convert_audio(input_path, output_path, output_format, quality='192k'):
    """Convert audio files"""
    try:
        # Map quality settings to bitrates
        quality_map = {
            'high': '320k',
            'medium': '192k', 
            'low': '128k'
        }
        bitrate = quality_map.get(quality, '192k')
        
        if output_format == 'mp3':
            cmd = ['ffmpeg', '-i', input_path, '-acodec', 'mp3', '-ab', bitrate, '-y', output_path]
        elif output_format == 'wav':
            cmd = ['ffmpeg', '-i', input_path, '-acodec', 'pcm_s16le', '-y', output_path]
        elif output_format == 'flac':
            cmd = ['ffmpeg', '-i', input_path, '-acodec', 'flac', '-y', output_path]
        elif output_format == 'aac':
            cmd = ['ffmpeg', '-i', input_path, '-acodec', 'aac', '-ab', bitrate, '-y', output_path]
        elif output_format == 'ogg':
            # OGG/Vorbis doesn't support -ab parameter, use -q:a instead
            quality_map_ogg = {
                'high': '6',      # Higher quality = lower number
                'medium': '4', 
                'low': '2'
            }
            ogg_quality = quality_map_ogg.get(quality, '4')
            cmd = ['ffmpeg', '-i', input_path, '-acodec', 'libvorbis', '-q:a', ogg_quality, '-y', output_path]
        else:
            return False
            
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"FFmpeg return code: {result.returncode}")
        if result.returncode == 0:
            print(f"Conversion successful: {output_path}")
            return True
        else:
            print(f"FFmpeg error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Audio conversion error: {e}")
        return False

def convert_video(input_path, output_path, output_format, quality='medium'):
    """Convert video files"""
    try:
        # Map quality settings to FFmpeg presets
        preset_map = {
            'high': 'slow',
            'medium': 'medium',
            'low': 'fast'
        }
        preset = preset_map.get(quality, 'medium')
        
        if output_format == 'mp4':
            cmd = ['ffmpeg', '-i', input_path, '-vcodec', 'libx264', '-acodec', 'aac', '-preset', preset, '-y', output_path]
        elif output_format == 'avi':
            cmd = ['ffmpeg', '-i', input_path, '-vcodec', 'libxvid', '-acodec', 'mp3', '-y', output_path]
        elif output_format == 'mov':
            cmd = ['ffmpeg', '-i', input_path, '-vcodec', 'libx264', '-acodec', 'aac', '-y', output_path]
        elif output_format == 'webm':
            cmd = ['ffmpeg', '-i', input_path, '-vcodec', 'libvpx', '-acodec', 'libvorbis', '-y', output_path]
        else:
            return False
            
        print(f"Running video conversion command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"FFmpeg return code: {result.returncode}")
        if result.returncode == 0:
            print(f"Video conversion successful: {output_path}")
            return True
        else:
            print(f"FFmpeg error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Video conversion error: {e}")
        return False

def extract_audio_from_video(input_path, output_path, output_format, quality='192k'):
    """Extract audio from video files"""
    try:
        # Map quality settings to bitrates
        quality_map = {
            'high': '320k',
            'medium': '192k', 
            'low': '128k'
        }
        bitrate = quality_map.get(quality, '192k')
        
        if output_format == 'mp3':
            cmd = ['ffmpeg', '-i', input_path, '-vn', '-acodec', 'mp3', '-ab', bitrate, '-y', output_path]
        elif output_format == 'wav':
            cmd = ['ffmpeg', '-i', input_path, '-vn', '-acodec', 'pcm_s16le', '-y', output_path]
        elif output_format == 'flac':
            cmd = ['ffmpeg', '-i', input_path, '-vn', '-acodec', 'flac', '-y', output_path]
        else:
            return False
            
        print(f"Running audio extraction command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"FFmpeg return code: {result.returncode}")
        if result.returncode == 0:
            print(f"Audio extraction successful: {output_path}")
            return True
        else:
            print(f"FFmpeg error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Audio extraction error: {e}")
        return False

def convert_image(input_path, output_path, output_format, quality=90):
    """Convert image files"""
    try:
        if output_format in ['jpg', 'jpeg']:
            cmd = ['ffmpeg', '-i', input_path, '-q:v', str(quality), '-y', output_path]
        elif output_format == 'png':
            cmd = ['ffmpeg', '-i', input_path, '-pngcompression', '9', '-y', output_path]
        elif output_format == 'webp':
            cmd = ['ffmpeg', '-i', input_path, '-quality', str(quality), '-y', output_path]
        else:
            return False
            
        print(f"Running image conversion command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"FFmpeg return code: {result.returncode}")
        if result.returncode == 0:
            print(f"Image conversion successful: {output_path}")
            return True
        else:
            print(f"FFmpeg error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Image conversion error: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    target_format = request.form.get('target_format')
    quality = request.form.get('quality', 'medium')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    if not target_format:
        return jsonify({'error': 'Target format not specified'}), 400
    
    # Generate unique filename
    original_ext = file.filename.rsplit('.', 1)[1].lower()
    unique_id = str(uuid.uuid4())
    input_filename = f"{unique_id}.{original_ext}"
    output_filename = f"{unique_id}.{target_format}"
    
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
    output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
    
    try:
        # Save uploaded file
        file.save(input_path)
        
        # Get file info
        file_info = get_file_info(input_path)
        
        # Determine conversion type and perform conversion
        success = False
        if file_info['type'] == 'audio':
            success = convert_audio(input_path, output_path, target_format, quality)
        elif file_info['type'] == 'video':
            if target_format in ['mp3', 'wav', 'flac', 'aac', 'ogg']:
                success = extract_audio_from_video(input_path, output_path, target_format, quality)
            else:
                success = convert_video(input_path, output_path, target_format, quality)
        elif file_info['type'] == 'image':
            # Map quality settings to numeric values for images
            quality_map_image = {
                'high': 95,
                'medium': 85, 
                'low': 75
            }
            image_quality = quality_map_image.get(quality, 85)
            success = convert_image(input_path, output_path, target_format, image_quality)
        
        if success and os.path.exists(output_path):
            # Clean up input file
            os.remove(input_path)
            
            return jsonify({
                'success': True,
                'message': 'File converted successfully',
                'download_url': f'/api/download/{output_filename}',
                'file_info': file_info
            })
        else:
            return jsonify({'error': 'Conversion failed'}), 500
            
    except Exception as e:
        # Clean up on error
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        return jsonify({'error': f'Conversion error: {str(e)}'}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['CONVERTED_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/formats')
def get_supported_formats():
    return jsonify({
        'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'],
        'video': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm'],
        'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']
    })

@app.route('/api/convert-from-path', methods=['POST'])
def convert_from_path():
    """Convert file from server file path"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        target_format = data.get('target_format')
        quality = data.get('quality', 'medium')
        
        if not file_path or not target_format:
            return jsonify({'error': 'File path and target format required'}), 400
        
        # Security: Only allow safe directories
        safe_directories = ['/home', '/media', '/mnt', '/tmp', os.getcwd()]
        if not any(file_path.startswith(safe_dir) for safe_dir in safe_directories):
            return jsonify({'error': 'File path not allowed for security reasons'}), 403
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            return jsonify({'error': 'File not readable'}), 403
        
        # Generate unique filename
        original_ext = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else ''
        unique_id = str(uuid.uuid4())
        input_filename = f"{unique_id}.{original_ext}"
        output_filename = f"{unique_id}.{target_format}"
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
        
        # Copy file to uploads directory
        import shutil
        shutil.copy2(file_path, input_path)
        
        # Get file info
        file_info = get_file_info(input_path)
        
        # Determine conversion type and perform conversion
        success = False
        if file_info['type'] == 'audio':
            success = convert_audio(input_path, output_path, target_format, quality)
        elif file_info['type'] == 'video':
            if target_format in ['mp3', 'wav', 'flac', 'aac', 'ogg']:
                success = extract_audio_from_video(input_path, output_path, target_format, quality)
            else:
                success = convert_video(input_path, output_path, target_format, quality)
        elif file_info['type'] == 'image':
            quality_map_image = {
                'high': 95,
                'medium': 85, 
                'low': 75
            }
            image_quality = quality_map_image.get(quality, 85)
            success = convert_image(input_path, output_path, target_format, image_quality)
        
        if success and os.path.exists(output_path):
            # Clean up input file
            os.remove(input_path)
            
            return jsonify({
                'success': True,
                'message': 'File converted successfully',
                'download_url': f'/api/download/{output_filename}',
                'file_info': file_info
            })
        else:
            return jsonify({'error': 'Conversion failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Conversion error: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
