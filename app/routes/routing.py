"""
Routing API endpoints
"""
from flask import Blueprint, request, jsonify
from app.services.routing_service import routing_service
from app.services.transfer_routing_service import transfer_routing_service

bp = Blueprint('routing', __name__)


@bp.route('/routes/direct', methods=['POST', 'OPTIONS'])
def find_direct_routes():
    """Find direct routes between two locations"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Request body is required'}), 400
        
        if 'start' not in data or 'end' not in data:
            return jsonify({'success': False, 'error': 'Both "start" and "end" locations are required'}), 400
        
        start = data['start']
        end = data['end']
        
        # Validate coordinates
        for location, name in [(start, 'start'), (end, 'end')]:
            for field in ['latitude', 'longitude']:
                if field not in location:
                    return jsonify({'success': False, 'error': f'Missing {field} in {name} location'}), 400
                if location[field] is None:
                    return jsonify({'success': False, 'error': f'{field} cannot be null in {name} location'}), 400
        
        try:
            start_lat = float(start['latitude'])
            start_lon = float(start['longitude'])
            end_lat = float(end['latitude'])
            end_lon = float(end['longitude'])
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Invalid coordinate format: coordinates must be numbers'}), 400
        
        if not (-90 <= start_lat <= 90) or not (-90 <= end_lat <= 90):
            return jsonify({'success': False, 'error': 'Latitude must be between -90 and 90'}), 400
        
        if not (-180 <= start_lon <= 180) or not (-180 <= end_lon <= 180):
            return jsonify({'success': False, 'error': 'Longitude must be between -180 and 180'}), 400
        
        routes = routing_service.find_direct_routes(start_lat, start_lon, end_lat, end_lon)
        valid_routes = [r for r in routes if r['valid']]
        
        return jsonify({
            'success': True,
            'start_location': {'latitude': start_lat, 'longitude': start_lon},
            'end_location': {'latitude': end_lat, 'longitude': end_lon},
            'routes_found': len(valid_routes),
            'routes': routes,
            'valid_routes_only': valid_routes
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Internal server error: {str(e)}'}), 500


@bp.route('/routes/search', methods=['POST', 'OPTIONS'])
def search_routes():
    """Find routes using addresses or coordinates"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Request body is required'}), 400
        
        if 'from' in data and 'to' in data:
            # ADDRESS-BASED SEARCH
            from app.services.geocoding_service import geocoding_service
            
            from_address = data['from']
            to_address = data['to']
            
            if not from_address or not from_address.strip():
                return jsonify({'success': False, 'error': 'From address cannot be empty'}), 400
            
            if not to_address or not to_address.strip():
                return jsonify({'success': False, 'error': 'To address cannot be empty'}), 400
            
            from_result = geocoding_service.geocode_address(from_address)
            if not from_result:
                return jsonify({
                    'success': False,
                    'error': f'Start address not found: {from_address}',
                    'suggestion': 'Try a more specific address or landmark in Greater Tunis'
                }), 404
            
            to_result = geocoding_service.geocode_address(to_address)
            if not to_result:
                return jsonify({
                    'success': False,
                    'error': f'End address not found: {to_address}',
                    'suggestion': 'Try a more specific address or landmark in Greater Tunis'
                }), 404
            
            start_lat = from_result['latitude']
            start_lon = from_result['longitude']
            end_lat = to_result['latitude']
            end_lon = to_result['longitude']
            
            routes = routing_service.find_direct_routes(start_lat, start_lon, end_lat, end_lon)
            valid_routes = [r for r in routes if r['valid']]
            
            return jsonify({
                'success': True,
                'from_address': {
                    'address': from_address,
                    'display_name': from_result['display_name'],
                    'coordinates': {'latitude': start_lat, 'longitude': start_lon}
                },
                'to_address': {
                    'address': to_address,
                    'display_name': to_result['display_name'],
                    'coordinates': {'latitude': end_lat, 'longitude': end_lon}
                },
                'routes_found': len(valid_routes),
                'routes': routes,
                'valid_routes_only': valid_routes
            }), 200
            
        elif 'start' in data and 'end' in data:
            # COORDINATE-BASED SEARCH
            start = data['start']
            end = data['end']
            
            for location, name in [(start, 'start'), (end, 'end')]:
                for field in ['latitude', 'longitude']:
                    if field not in location:
                        return jsonify({'success': False, 'error': f'Missing {field} in {name} location'}), 400
                    if location[field] is None:
                        return jsonify({'success': False, 'error': f'{field} cannot be null in {name} location'}), 400
            
            try:
                start_lat = float(start['latitude'])
                start_lon = float(start['longitude'])
                end_lat = float(end['latitude'])
                end_lon = float(end['longitude'])
            except (ValueError, TypeError):
                return jsonify({'success': False, 'error': 'Invalid coordinate format'}), 400
            
            routes = routing_service.find_direct_routes(start_lat, start_lon, end_lat, end_lon)
            valid_routes = [r for r in routes if r['valid']]
            
            return jsonify({
                'success': True,
                'start_location': {'latitude': start_lat, 'longitude': start_lon},
                'end_location': {'latitude': end_lat, 'longitude': end_lon},
                'routes_found': len(valid_routes),
                'routes': routes,
                'valid_routes_only': valid_routes
            }), 200
        
        else:
            return jsonify({
                'success': False,
                'error': 'Request must include either ("from" and "to") OR ("start" and "end")'
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Internal server error: {str(e)}'}), 500


@bp.route('/routes/transfer', methods=['POST', 'OPTIONS'])
def find_transfer_routes():
    """Find routes with one transfer between two buses"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Request body is required'}), 400
        
        max_results = data.get('max_results', 10)
        
        if not isinstance(max_results, int) or max_results < 1 or max_results > 20:
            return jsonify({'success': False, 'error': 'max_results must be an integer between 1 and 20'}), 400
        
        if 'from' in data and 'to' in data:
            # ADDRESS-BASED SEARCH
            from app.services.geocoding_service import geocoding_service
            
            from_address = data['from']
            to_address = data['to']
            
            if not from_address or not from_address.strip():
                return jsonify({'success': False, 'error': 'From address cannot be empty'}), 400
            
            if not to_address or not to_address.strip():
                return jsonify({'success': False, 'error': 'To address cannot be empty'}), 400
            
            from_result = geocoding_service.geocode_address(from_address)
            if not from_result:
                return jsonify({
                    'success': False,
                    'error': f'Start address not found: {from_address}',
                    'suggestion': 'Try a more specific address or landmark in Greater Tunis'
                }), 404
            
            to_result = geocoding_service.geocode_address(to_address)
            if not to_result:
                return jsonify({
                    'success': False,
                    'error': f'End address not found: {to_address}',
                    'suggestion': 'Try a more specific address or landmark in Greater Tunis'
                }), 404
            
            start_lat = from_result['latitude']
            start_lon = from_result['longitude']
            end_lat = to_result['latitude']
            end_lon = to_result['longitude']
            
            routes = transfer_routing_service.find_transfer_routes(
                start_lat, start_lon, end_lat, end_lon, max_results=max_results
            )
            
            return jsonify({
                'success': True,
                'from_address': {
                    'address': from_address,
                    'display_name': from_result['display_name'],
                    'coordinates': {'latitude': start_lat, 'longitude': start_lon}
                },
                'to_address': {
                    'address': to_address,
                    'display_name': to_result['display_name'],
                    'coordinates': {'latitude': end_lat, 'longitude': end_lon}
                },
                'routes_found': len(routes),
                'routes': routes
            }), 200
            
        elif 'start' in data and 'end' in data:
            # COORDINATE-BASED SEARCH
            start = data['start']
            end = data['end']
            
            for location, name in [(start, 'start'), (end, 'end')]:
                for field in ['latitude', 'longitude']:
                    if field not in location:
                        return jsonify({'success': False, 'error': f'Missing {field} in {name} location'}), 400
                    if location[field] is None:
                        return jsonify({'success': False, 'error': f'{field} cannot be null in {name} location'}), 400
            
            try:
                start_lat = float(start['latitude'])
                start_lon = float(start['longitude'])
                end_lat = float(end['latitude'])
                end_lon = float(end['longitude'])
            except (ValueError, TypeError):
                return jsonify({'success': False, 'error': 'Invalid coordinate format'}), 400
            
            if not (-90 <= start_lat <= 90) or not (-90 <= end_lat <= 90):
                return jsonify({'success': False, 'error': 'Latitude must be between -90 and 90'}), 400
            
            if not (-180 <= start_lon <= 180) or not (-180 <= end_lon <= 180):
                return jsonify({'success': False, 'error': 'Longitude must be between -180 and 180'}), 400
            
            routes = transfer_routing_service.find_transfer_routes(
                start_lat, start_lon, end_lat, end_lon, max_results=max_results
            )
            
            return jsonify({
                'success': True,
                'start_location': {'latitude': start_lat, 'longitude': start_lon},
                'end_location': {'latitude': end_lat, 'longitude': end_lon},
                'routes_found': len(routes),
                'routes': routes
            }), 200
        
        else:
            return jsonify({
                'success': False,
                'error': 'Request must include either ("from" and "to") OR ("start" and "end")'
            }), 400
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Internal server error: {str(e)}'}), 500
@bp.route('/routes/walking-path', methods=['POST', 'OPTIONS'])
def get_walking_path():
    """Get realistic walking path between two points using OSRM"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400
        
        start_lat = data.get('start_lat')
        start_lon = data.get('start_lon')
        end_lat = data.get('end_lat')
        end_lon = data.get('end_lon')
        
        if None in [start_lat, start_lon, end_lat, end_lon]:
            return jsonify({'success': False, 'error': 'Missing coordinates'}), 400
        
        from app.services.walking_service import walking_service
        
        path_result = walking_service.get_walking_route(
            float(start_lat), float(start_lon),
            float(end_lat), float(end_lon)
        )
        
        if path_result:
            return jsonify({
                'success': True,
                'path': path_result['path'],
                'distance_meters': path_result['distance_meters'],
                'duration_minutes': path_result['duration_minutes']
            }), 200
        else:
            # Return straight line fallback
            return jsonify({
                'success': True,
                'path': [[float(start_lat), float(start_lon)], [float(end_lat), float(end_lon)]],
                'fallback': True
            }), 200
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500