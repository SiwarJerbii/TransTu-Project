"""
TransTu Project - Application Factory
Creates and configures the Flask application
"""

from flask import Flask
from flask_cors import CORS
from config import config
import os

def create_app(config_name=None):
    """
    Application factory pattern
    Creates and configures the Flask app
    """
    
    # Use environment variable or default to development
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    from app.routes import health, geocoding, routing
    
    app.register_blueprint(health.bp)
    app.register_blueprint(geocoding.bp, url_prefix='/api')  # NEW
    app.register_blueprint(routing.bp, url_prefix='/api')
    
    return app