"""
Health check endpoint
"""

from flask import Blueprint, jsonify, render_template

bp = Blueprint('health', __name__)

@bp.route('/', methods=['GET'])
def index():
    """
    Serve the main index.html page
    """
    return render_template('index.html')

@bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    Returns API status
    """
    return jsonify({
        'status': 'ok',
        'message': 'TransTu API is running',
        'version': '1.0.0'
    }), 200