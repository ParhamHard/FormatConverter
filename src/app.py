"""
Main Flask application factory for the Media Converter service.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from flask_cors import CORS

from .config import get_config
from .routes import api_bp, web_bp
from .utils.ffmpeg_utils import check_ffmpeg_available


def create_app(config_name: str = None) -> Flask:
    """
    Create and configure Flask application.
    
    Args:
        config_name: Configuration name to use
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Setup logging
    setup_logging(app, config)
    
    # Setup CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Basic health check endpoint."""
        return jsonify({'status': 'healthy', 'service': 'media-converter'})
    
    # Check FFmpeg availability on startup
    with app.app_context():
        check_ffmpeg_startup()
    
    return app


def setup_logging(app: Flask, config) -> None:
    """Setup application logging."""
    if not app.debug and not app.testing:
        # Production logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            config.LOG_FILE, 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Media Converter startup')
    else:
        # Development logging
        app.logger.setLevel(logging.DEBUG)


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request could not be processed.',
            'status_code': 400
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found.',
            'status_code': 404
        }), 404
    
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            'error': 'File Too Large',
            'message': 'The uploaded file exceeds the maximum allowed size.',
            'status_code': 413
        }), 413
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred.',
            'status_code': 500
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {error}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred.',
            'status_code': 500
        }), 500


def check_ffmpeg_startup() -> None:
    """Check FFmpeg availability on application startup."""
    is_available, error_msg = check_ffmpeg_available()
    
    if not is_available:
        logging.error(f"FFmpeg not available: {error_msg}")
        logging.error("Media conversion functionality will not work properly")
    else:
        logging.info("FFmpeg is available and ready for media conversion")


# For development server
if __name__ == '__main__':
    app = create_app()
    config = app.config
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )

