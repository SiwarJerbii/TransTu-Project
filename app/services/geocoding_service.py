"""
Geocoding Service - Convert addresses to coordinates
Uses Nominatim (OpenStreetMap) API
"""
import requests
import time
from typing import Optional, Dict, Tuple

class GeocodingService:
    """Service for converting addresses to geographic coordinates"""
    
    # Nominatim API configuration
    BASE_URL = "https://nominatim.openstreetmap.org/search"
    USER_AGENT = "TransTuRouteApp/1.0"
    COUNTRY_CODE = "tn"  # Tunisia
    
    # Rate limiting
    LAST_REQUEST_TIME = 0
    MIN_REQUEST_INTERVAL = 1.0  # seconds between requests (Nominatim policy)
    
    @classmethod
    def geocode_address(cls, address: str) -> Optional[Dict]:
        """
        Convert address to coordinates using Nominatim API
        
        Args:
            address: Address string (e.g., "Avenue Habib Bourguiba, Tunis")
        
        Returns:
            Dict with coordinates and metadata, or None if not found
            {
                'latitude': float,
                'longitude': float,
                'display_name': str,
                'address': str
            }
        """
        # Validate input
        if not address or not address.strip():
            return None
        
        # Rate limiting - respect Nominatim's usage policy
        cls._wait_for_rate_limit()
        
        # Prepare request
        params = {
            'q': address.strip(),
            'format': 'json',
            'limit': 1,
            'countrycodes': cls.COUNTRY_CODE
        }
        
        headers = {
            'User-Agent': cls.USER_AGENT
        }
        
        try:
            response = requests.get(
                cls.BASE_URL, 
                params=params, 
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            results = response.json()
            
            if results and len(results) > 0:
                result = results[0]
                
                return {
                    'latitude': float(result['lat']),
                    'longitude': float(result['lon']),
                    'display_name': result['display_name'],
                    'address': address,
                    'type': result.get('type', 'unknown'),
                    'importance': result.get('importance', 0)
                }
            
            return None
            
        except requests.RequestException as e:
            print(f"Geocoding API error: {e}")
            return None
        except (KeyError, ValueError) as e:
            print(f"Geocoding parse error: {e}")
            return None
    
    @classmethod
    def _wait_for_rate_limit(cls):
        """
        Ensure we don't exceed Nominatim's rate limit (1 request per second)
        """
        current_time = time.time()
        time_since_last = current_time - cls.LAST_REQUEST_TIME
        
        if time_since_last < cls.MIN_REQUEST_INTERVAL:
            sleep_time = cls.MIN_REQUEST_INTERVAL - time_since_last
            time.sleep(sleep_time)
        
        cls.LAST_REQUEST_TIME = time.time()
    
    @classmethod
    def geocode_multiple(cls, addresses: list) -> Dict[str, Optional[Dict]]:
        """
        Geocode multiple addresses
        
        Args:
            addresses: List of address strings
        
        Returns:
            Dict mapping address to geocoding result
        """
        results = {}
        
        for address in addresses:
            results[address] = cls.geocode_address(address)
            
        return results


# Create service instance
geocoding_service = GeocodingService()