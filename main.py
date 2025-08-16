#!/usr/bin/env python3
"""
Main entry point for the Media Converter service.
This file provides backward compatibility and can be used for development.
"""

import os
import sys

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import create_app

if __name__ == '__main__':
    app = create_app()
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
