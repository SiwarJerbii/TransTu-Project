"""
Geocoding API endpoints
"""
from flask import Blueprint, request, jsonify
from app.services.geocoding_service import geocoding_service

bp = Blueprint('geocoding', __name__)

@bp.route('/geocode', methods=['POST', 'OPTIONS'])
def geocode_address():
    """
    Convert address to coordinates
    
    Request Body:
    {
        "address": "Avenue Habib Bourguiba, Tunis"
    }
    
    Response:
    {
        "success": true,
        "address": "Avenue Habib Bourguiba, Tunis",
        "coordinates": {
            "latitude": 36.8065,
            "longitude": 10.1815
        },
        "display_name": "Avenue Habib Bourguiba, Tunis, Tunisia",
        "type": "road"
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
        
        # Validate address field
        if 'address' not in data:
            return jsonify({
                'success': False,
                'error': 'Address field is required'
            }), 400
        
        address = data['address']
        
        # Validate address is not empty
        if not address or not address.strip():
            return jsonify({
                'success': False,
                'error': 'Address cannot be empty'
            }), 400
        
        # Geocode the address
        result = geocoding_service.geocode_address(address)
        
        # Check if address was found
        if not result:
            return jsonify({
                'success': False,
                'error': 'Address not found',
                'address': address,
                'suggestion': 'Try a more specific address or landmark in Greater Tunis'
            }), 404
        
        # Return successful result
        return jsonify({
            'success': True,
            'address': result['address'],
            'coordinates': {
                'latitude': result['latitude'],
                'longitude': result['longitude']
            },
            'display_name': result['display_name'],
            'type': result.get('type'),
            'importance': result.get('importance')
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@bp.route('/geocode/batch', methods=['POST', 'OPTIONS'])
def geocode_multiple_addresses():
    """
    Geocode multiple addresses at once
    
    Request Body:
    {
        "addresses": [
            "Avenue Habib Bourguiba, Tunis",
            "Carthage, Tunisia"
        ]
    }
    
    Response:
    {
        "success": true,
        "results": [
            {
                "address": "...",
                "coordinates": {...},
                "found": true
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'addresses' not in data:
            return jsonify({
                'success': False,
                'error': 'Addresses array is required'
            }), 400
        
        addresses = data['addresses']
        
        if not isinstance(addresses, list):
            return jsonify({
                'success': False,
                'error': 'Addresses must be an array'
            }), 400
        
        if len(addresses) > 10:
            return jsonify({
                'success': False,
                'error': 'Maximum 10 addresses per batch request'
            }), 400
        
        # Geocode all addresses
        results = []
        
        for address in addresses:
            result = geocoding_service.geocode_address(address)
            
            if result:
                results.append({
                    'address': address,
                    'coordinates': {
                        'latitude': result['latitude'],
                        'longitude': result['longitude']
                    },
                    'display_name': result['display_name'],
                    'found': True
                })
            else:
                results.append({
                    'address': address,
                    'found': False,
                    'error': 'Address not found'
                })
        
        return jsonify({
            'success': True,
            'total': len(addresses),
            'found': sum(1 for r in results if r['found']),
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500