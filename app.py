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
            # Audio file
            audio = File(filepath)
            if audio:
                duration = audio.info.length if hasattr(audio.info, 'length') else None
                return {
                    'type': 'audio',
                    'duration': duration,
                    'size': os.path.getsize(filepath)
                }
        elif filepath.lower().endswith(('.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm')):
            # Video file
            probe = ffmpeg.probe(filepath)
            if probe:
                video_info = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                audio_info = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
                return {
                    'type': 'video',
                    'duration': float(probe['format']['duration']) if 'duration' in probe['format'] else None,
                    'width': int(video_info['width']) if video_info else None,
                    'height': int(video_info['height']) if video_info else None,
                    'size': os.path.getsize(filepath)
                }
        elif filepath.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')):
            # Image file
            probe = ffmpeg.probe(filepath)
            if probe:
                video_info = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                return {
                    'type': 'image',
                    'width': int(video_info['width']) if video_info else None,
                    'height': int(video_info['height']) if video_info else None,
                    'size': os.path.getsize(filepath)
                }
    except Exception as e:
        print(f"Error getting file info: {e}")
    
    return {'type': 'unknown', 'size': os.path.getsize(filepath)}

def convert_audio(input_path, output_path, output_format, quality='192k'):
    """Convert audio files"""
    try:
        if output_format == 'mp3':
            ffmpeg.input(input_path).output(output_path, acodec='mp3', ab=quality).run(overwrite_output=True, quiet=True)
        elif output_format == 'wav':
            ffmpeg.input(input_path).output(output_path, acodec='pcm_s16le').run(overwrite_output=True, quiet=True)
        elif output_format == 'flac':
            ffmpeg.input(input_path).output(output_path, acodec='flac').run(overwrite_output=True, quiet=True)
        elif output_format == 'aac':
            ffmpeg.input(input_path).output(output_path, acodec='aac', ab=quality).run(overwrite_output=True, quiet=True)
        elif output_format == 'ogg':
            ffmpeg.input(input_path).output(output_path, acodec='libvorbis', ab=quality).run(overwrite_output=True, quiet=True)
        return True
    except Exception as e:
        print(f"Audio conversion error: {e}")
        return False

def convert_video(input_path, output_path, output_format, quality='medium'):
    """Convert video files"""
    try:
        if output_format == 'mp4':
            ffmpeg.input(input_path).output(output_path, vcodec='libx264', acodec='aac', preset=quality).run(overwrite_output=True, quiet=True)
        elif output_format == 'avi':
            ffmpeg.input(input_path).output(output_path, vcodec='libxvid', acodec='mp3').run(overwrite_output=True, quiet=True)
        elif output_format == 'mov':
            ffmpeg.input(input_path).output(output_path, vcodec='libx264', acodec='aac').run(overwrite_output=True, quiet=True)
        elif output_format == 'webm':
            ffmpeg.input(input_path).output(output_path, vcodec='libvpx', acodec='libvorbis').run(overwrite_output=True, quiet=True)
        return True
    except Exception as e:
        print(f"Video conversion error: {e}")
        return False

def extract_audio_from_video(input_path, output_path, output_format, quality='192k'):
    """Extract audio from video files"""
    try:
        if output_format == 'mp3':
            ffmpeg.input(input_path).output(output_path, vn=None, acodec='mp3', ab=quality).run(overwrite_output=True, quiet=True)
        elif output_format == 'wav':
            ffmpeg.input(input_path).output(output_path, vn=None, acodec='pcm_s16le').run(overwrite_output=True, quiet=True)
        elif output_format == 'flac':
            ffmpeg.input(input_path).output(output_path, vn=None, acodec='flac').run(overwrite_output=True, quiet=True)
        return True
    except Exception as e:
        print(f"Audio extraction error: {e}")
        return False

def convert_image(input_path, output_path, output_format, quality=90):
    """Convert image files"""
    try:
        if output_format in ['jpg', 'jpeg']:
            ffmpeg.input(input_path).output(output_path, q=f'v={quality}').run(overwrite_output=True, quiet=True)
        elif output_format == 'png':
            ffmpeg.input(input_path).output(output_path, pngcompression=9).run(overwrite_output=True, quiet=True)
        elif output_format == 'webp':
            ffmpeg.input(input_path).output(output_path, quality=quality).run(overwrite_output=True, quiet=True)
        return True
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
            success = convert_image(input_path, output_path, target_format, int(quality) if quality.isdigit() else 90)
        
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

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
