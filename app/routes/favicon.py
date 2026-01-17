"""
Favicon route
"""

from flask import Blueprint, send_from_directory
import os

bp = Blueprint('favicon', __name__)

@bp.route('/favicon.ico')
def favicon():
    """
    Serve favicon
    """
    # Return a simple 204 No Content response to avoid 404
    return '', 204
