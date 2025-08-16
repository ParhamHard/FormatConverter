"""
Web routes for the Media Converter service.
"""

from flask import Blueprint, render_template, current_app

# Create blueprint
web_bp = Blueprint('web', __name__)


@web_bp.route('/')
def index():
    """
    Main web interface for file conversion.
    
    Returns:
        Rendered HTML template
    """
    return render_template('index.html')


@web_bp.route('/about')
def about():
    """
    About page for the service.
    
    Returns:
        Rendered HTML template
    """
    return render_template('about.html')


@web_bp.route('/help')
def help_page():
    """
    Help and documentation page.
    
    Returns:
        Rendered HTML template
    """
    return render_template('help.html')

