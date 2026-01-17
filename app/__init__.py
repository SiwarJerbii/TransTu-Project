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
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Get the parent directory (project root) for template path
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app, 
         resources={r"/api/*": {"origins": "*"}},
         supports_credentials=False,
         methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
         allow_headers=["Content-Type", "Authorization"],
         expose_headers=["Content-Type"],
         max_age=3600)
    
    # Register API blueprints
    from app.routes import health, geocoding, routing, favicon
    
    app.register_blueprint(health.bp)
    app.register_blueprint(geocoding.bp, url_prefix='/api')
    app.register_blueprint(routing.bp, url_prefix='/api')
    app.register_blueprint(favicon.bp)
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    return app