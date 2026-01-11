"""
TransTu Project - Application Entry Point
Run this file to start the Flask development server
"""

from app import create_app
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app()

if __name__ == '__main__':
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    print("=" * 70)
    print(" 🚌 TransTu API Server")
    print("=" * 70)
    print(f" Running on: http://{host}:{port}")
    print(f" Debug mode: {debug}")
    print("=" * 70)
    
    app.run(host=host, port=port, debug=debug)