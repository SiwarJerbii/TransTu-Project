"""
Routing Service - Find routes between locations
"""
from typing import Dict, List, Optional, Tuple
from app.services.distance_service import distance_service
from app.utils.data_loader import data_loader

class RoutingService:
    """Service for finding bus routes between locations"""
    
    def __init__(self, max_walking_distance: int = 500):
        """
        Initialize routing service
        
        Args:
            max_walking_distance: Maximum walking distance in meters (default 500m)
        """
        self.max_walking_distance = max_walking_distance
        self.bus_data = data_loader.load_bus_data()
    
    def find_nearest_stop(self, lat: float, lon: float, 
                         route: Dict) -> Optional[Dict]:
        """
        Find the nearest stop to given coordinates on a specific route
        
        Args:
            lat, lon: User coordinates
            route: Bus route dictionary
        
        Returns:
            Nearest stop with distance, or None if none within max_walking_distance
        """
        nearest = None
        min_distance = float('inf')
        
        for stop in route['stops']:
            distance = distance_service.haversine_distance(
                lat, lon, 
                stop['latitude'], stop['longitude']
            )
            
            if distance < min_distance and distance <= self.max_walking_distance:
                min_distance = distance
                nearest = {
                    **stop,
                    'distance': round(distance)
                }
        
        return nearest
    
    def can_travel_between_stops(self, route: Dict, 
                                 start_stop: Dict, 
                                 end_stop: Dict) -> Dict:
        """
        Validate if user can travel between two stops on a route
        
        Args:
            route: Bus route dictionary
            start_stop: Starting stop
            end_stop: Ending stop
        
        Returns:
            Dict with validation result:
            {
                'valid': bool,
                'reason': str (if invalid),
                'stops_count': int (if valid),
                'estimated_minutes': int (if valid)
            }
        """
        if not start_stop or not end_stop:
            return {
                'valid': False,
                'reason': 'Stop not found on this route'
            }
        
        start_number = start_stop['stop_number']
        end_number = end_stop['stop_number']
        
        # Check if same stop
        if start_number == end_number:
            return {
                'valid': False,
                'reason': 'Start and end are the same stop'
            }
        
        # Check direction (must travel forward: increasing stop numbers)
        if end_number > start_number:
            stops_count = end_number - start_number
            estimated_minutes = distance_service.estimate_bus_duration(stops_count)
            
            return {
                'valid': True,
                'stops_count': stops_count,
                'estimated_minutes': estimated_minutes
            }
        else:
            return {
                'valid': False,
                'reason': 'Would require traveling backwards (try opposite direction)'
            }
    
    def find_direct_routes(self, start_lat: float, start_lon: float,
                          end_lat: float, end_lon: float) -> List[Dict]:
        """
        Find all direct routes (no transfers) between two locations
        
        Args:
            start_lat, start_lon: Starting coordinates
            end_lat, end_lon: Ending coordinates
        
        Returns:
            List of route options with validation results
        """
        results = []
        
        for route in self.bus_data['routes']:
            # Find nearest stops at start and end locations
            start_stop = self.find_nearest_stop(start_lat, start_lon, route)
            end_stop = self.find_nearest_stop(end_lat, end_lon, route)
            
            if start_stop and end_stop:
                # Validate if travel is possible
                validation = self.can_travel_between_stops(route, start_stop, end_stop)
                
                # Calculate walking distances and times
                walking_to_start = start_stop['distance']
                walking_to_end = end_stop['distance']
                walking_time_start = round(
                    distance_service.calculate_walking_time(walking_to_start)
                )
                walking_time_end = round(
                    distance_service.calculate_walking_time(walking_to_end)
                )
                
                # Calculate total time if valid
                total_time = None
                if validation['valid']:
                    total_time = (
                        walking_time_start + 
                        validation['estimated_minutes'] + 
                        walking_time_end
                    )
                
                results.append({
                    'bus_line': route['bus_name'],
                    'direction': route['direction'],
                    'route_id': route['id'],
                    'valid': validation['valid'],
                    'start_stop': {
                        'name': start_stop['stop_name'],
                        'number': start_stop['stop_number'],
                        'coordinates': {
                            'latitude': start_stop['latitude'],
                            'longitude': start_stop['longitude']
                        }
                    },
                    'end_stop': {
                        'name': end_stop['stop_name'],
                        'number': end_stop['stop_number'],
                        'coordinates': {
                            'latitude': end_stop['latitude'],
                            'longitude': end_stop['longitude']
                        }
                    },
                    'walking': {
                        'to_start_meters': walking_to_start,
                        'to_start_minutes': walking_time_start,
                        'from_end_meters': walking_to_end,
                        'from_end_minutes': walking_time_end
                    },
                    'validation': validation,
                    'total_time_minutes': total_time
                })
        
        # Sort results: valid routes first, then by total time
        results.sort(key=lambda x: (
            not x['valid'],  # Valid routes first
            x['total_time_minutes'] if x['total_time_minutes'] else float('inf')
        ))
        
        return results


# Create service instance
routing_service = RoutingService()