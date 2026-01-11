"""
Health check endpoint
"""

from flask import Blueprint, jsonify

bp = Blueprint('health', __name__)

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