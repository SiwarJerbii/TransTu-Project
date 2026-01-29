"""
Walking Service - Get realistic walking routes using OSRM API
"""
import requests
from typing import Optional, Dict, List, Tuple

class WalkingService:
    """Service for getting realistic walking routes via OSRM"""
    
    # OSRM Demo server (free, no API key needed)
    BASE_URL = "https://router.project-osrm.org/route/v1/foot"
    
    @classmethod
    def get_walking_route(cls, start_lat: float, start_lon: float, 
                          end_lat: float, end_lon: float) -> Optional[Dict]:
        """
        Get realistic walking route between two points
        
        Args:
            start_lat, start_lon: Starting coordinates
            end_lat, end_lon: Ending coordinates
        
        Returns:
            Dict with distance, duration, and geometry (list of coordinates)
        """
        try:
            # OSRM expects coordinates as lon,lat (reversed!)
            url = f"{cls.BASE_URL}/{start_lon},{start_lat};{end_lon},{end_lat}"
            
            params = {
                'overview': 'full',      # Get full route geometry
                'geometries': 'geojson', # Return as GeoJSON coordinates
                'steps': 'false'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['code'] != 'Ok' or not data['routes']:
                return None
            
            route = data['routes'][0]
            
            # Extract coordinates (OSRM returns [lon, lat], we need [lat, lon])
            coordinates = route['geometry']['coordinates']
            path = [[coord[1], coord[0]] for coord in coordinates]  # Flip to [lat, lon]
            
            return {
                'distance_meters': round(route['distance']),
                'duration_minutes': round(route['duration'] / 60, 1),
                'path': path  # List of [lat, lon] coordinates
            }
            
        except requests.RequestException as e:
            print(f"OSRM API error: {e}")
            return None
        except (KeyError, IndexError) as e:
            print(f"OSRM parse error: {e}")
            return None
    
    @classmethod
    def get_straight_line_fallback(cls, start_lat: float, start_lon: float,
                                    end_lat: float, end_lon: float) -> Dict:
        """
        Fallback: Return straight line if OSRM fails
        """
        from app.services.distance_service import distance_service
        
        distance = distance_service.haversine_distance(
            start_lat, start_lon, end_lat, end_lon
        )
        walking_time = distance_service.calculate_walking_time(distance)
        
        return {
            'distance_meters': round(distance),
            'duration_minutes': round(walking_time, 1),
            'path': [
                [start_lat, start_lon],
                [end_lat, end_lon]
            ]
        }


# Create service instance
walking_service = WalkingService()