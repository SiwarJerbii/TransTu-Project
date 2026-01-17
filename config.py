"""
TransTu Project - Configuration
Centralized configuration for all environments
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Data paths
    BUS_DATA_PATH = BASE_DIR / os.getenv('BUS_DATA_PATH', 'data/bus_routes.json')
    METRO_DATA_PATH = BASE_DIR / os.getenv('METRO_DATA_PATH', 'data/metro_routes.json')
    TGM_DATA_PATH = BASE_DIR / os.getenv('TGM_DATA_PATH', 'data/tgm_routes.json')
    
    # API Configuration
    NOMINATIM_USER_AGENT = os.getenv('NOMINATIM_USER_AGENT', 'TransTuRouteApp/1.0')
    OSRM_BASE_URL = os.getenv('OSRM_BASE_URL', 'http://router.project-osrm.org/route/v1')
    
    # Route Calculation
    MAX_WALKING_DISTANCE = int(os.getenv('MAX_WALKING_DISTANCE', 500))
    WALKING_SPEED = int(os.getenv('WALKING_SPEED', 80))  # meters per minute
    API_DELAY = float(os.getenv('API_DELAY', 1))  # seconds
    
    # CORS
    CORS_ORIGINS = ['*']

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}