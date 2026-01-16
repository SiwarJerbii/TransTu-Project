"""
Routing API endpoints
"""
from flask import Blueprint, request, jsonify
from app.services.routing_service import routing_service

bp = Blueprint('routing', __name__)

@bp.route('/routes/direct', methods=['POST'])
def find_direct_routes():
    """
    Find direct routes between two locations
    
    Request Body:
    {
        "start": {
            "latitude": 36.8065,
            "longitude": 10.1815
        },
        "end": {
            "latitude": 36.7518,
            "longitude": 9.9800
        }
    }
    
    Response:
    {
        "success": true,
        "start_location": {...},
        "end_location": {...},
        "routes": [...]
    }
    """
    try:
        # Validate request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Validate required fields
        if 'start' not in data or 'end' not in data:
            return jsonify({
                'success': False,
                'error': 'Both "start" and "end" locations are required'
            }), 400
        
        start = data['start']
        end = data['end']
        
        # Validate coordinates
        required_fields = ['latitude', 'longitude']
        for location, name in [(start, 'start'), (end, 'end')]:
            for field in required_fields:
                if field not in location:
                    return jsonify({
                        'success': False,
                        'error': f'Missing {field} in {name} location'
                    }), 400
        
        # Extract coordinates
        start_lat = float(start['latitude'])
        start_lon = float(start['longitude'])
        end_lat = float(end['latitude'])
        end_lon = float(end['longitude'])
        
        # Validate coordinate ranges
        if not (-90 <= start_lat <= 90) or not (-90 <= end_lat <= 90):
            return jsonify({
                'success': False,
                'error': 'Latitude must be between -90 and 90'
            }), 400
        
        if not (-180 <= start_lon <= 180) or not (-180 <= end_lon <= 180):
            return jsonify({
                'success': False,
                'error': 'Longitude must be between -180 and 180'
            }), 400
        
        # Find routes
        routes = routing_service.find_direct_routes(
            start_lat, start_lon,
            end_lat, end_lon
        )
        
        # Filter to only valid routes (optional - can show all)
        valid_routes = [r for r in routes if r['valid']]
        
        return jsonify({
            'success': True,
            'start_location': {
                'latitude': start_lat,
                'longitude': start_lon
            },
            'end_location': {
                'latitude': end_lat,
                'longitude': end_lon
            },
            'routes_found': len(valid_routes),
            'routes': routes,  # Include all routes (valid + invalid)
            'valid_routes_only': valid_routes
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid coordinate format: {str(e)}'
        }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500