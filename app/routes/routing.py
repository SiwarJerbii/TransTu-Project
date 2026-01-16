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
        
        # Validate coordinates exist
        required_fields = ['latitude', 'longitude']
        for location, name in [(start, 'start'), (end, 'end')]:
            for field in required_fields:
                if field not in location:
                    return jsonify({
                        'success': False,
                        'error': f'Missing {field} in {name} location'
                    }), 400
                
                # NEW: Check for null values BEFORE trying to convert
                if location[field] is None:
                    return jsonify({
                        'success': False,
                        'error': f'{field} cannot be null in {name} location'
                    }), 400
        
        # Extract and validate coordinates
        try:
            start_lat = float(start['latitude'])
            start_lon = float(start['longitude'])
            end_lat = float(end['latitude'])
            end_lon = float(end['longitude'])
        except (ValueError, TypeError) as e:
            return jsonify({
                'success': False,
                'error': f'Invalid coordinate format: coordinates must be numbers'
            }), 400
        
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
        
        # Filter to only valid routes
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
            'routes': routes,
            'valid_routes_only': valid_routes
        }), 200
        
    except Exception as e:
        # Catch any unexpected errors
        # In production, log this to a file/monitoring service
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500
@bp.route('/routes/search', methods=['POST'])
def search_routes():
    """
    Find routes using addresses or coordinates
    
    Request Body (Option 1 - Addresses):
    {
        "from": "Avenue Habib Bourguiba, Tunis",
        "to": "Carthage, Tunisia"
    }
    
    Request Body (Option 2 - Coordinates):
    {
        "start": {"latitude": 36.8065, "longitude": 10.1815},
        "end": {"latitude": 36.8531, "longitude": 10.3239}
    }
    
    Response: Same as /routes/direct
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Check if using addresses (from/to) or coordinates (start/end)
        if 'from' in data and 'to' in data:
            # Address-based search
            from app.services.geocoding_service import geocoding_service
            
            from_address = data['from']
            to_address = data['to']
            
            # Geocode start address
            from_result = geocoding_service.geocode_address(from_address)
            if not from_result:
                return jsonify({
                    'success': False,
                    'error': f'Start address not found: {from_address}'
                }), 404
            
            # Geocode end address
            to_result = geocoding_service.geocode_address(to_address)
            if not to_result:
                return jsonify({
                    'success': False,
                    'error': f'End address not found: {to_address}'
                }), 404
            
            # Extract coordinates
            start_lat = from_result['latitude']
            start_lon = from_result['longitude']
            end_lat = to_result['latitude']
            end_lon = to_result['longitude']
            
            # Find routes
            routes = routing_service.find_direct_routes(
                start_lat, start_lon,
                end_lat, end_lon
            )
            
            valid_routes = [r for r in routes if r['valid']]
            
            return jsonify({
                'success': True,
                'from_address': {
                    'address': from_address,
                    'display_name': from_result['display_name'],
                    'coordinates': {
                        'latitude': start_lat,
                        'longitude': start_lon
                    }
                },
                'to_address': {
                    'address': to_address,
                    'display_name': to_result['display_name'],
                    'coordinates': {
                        'latitude': end_lat,
                        'longitude': end_lon
                    }
                },
                'routes_found': len(valid_routes),
                'routes': routes,
                'valid_routes_only': valid_routes
            }), 200
            
        elif 'start' in data and 'end' in data:
            # Coordinate-based search (existing functionality)
            return find_direct_routes()
        
        else:
            return jsonify({
                'success': False,
                'error': 'Request must include either ("from" and "to") or ("start" and "end")'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500