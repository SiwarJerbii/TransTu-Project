"""
Distance Service - Calculate distances between coordinates
"""
import math
from typing import Tuple

class DistanceService:
    """Service for calculating distances between geographic points"""
    
    EARTH_RADIUS_METERS = 6371000
    WALKING_SPEED_M_PER_MIN = 80  # Average walking speed
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """
        Calculate straight-line distance between two points using Haversine formula
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
        
        Returns:
            Distance in meters
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = DistanceService.EARTH_RADIUS_METERS * c
        return distance
    
    @staticmethod
    def calculate_walking_time(distance_meters: float) -> float:
        """
        Calculate walking time based on distance
        
        Args:
            distance_meters: Distance in meters
        
        Returns:
            Walking time in minutes
        """
        return distance_meters / DistanceService.WALKING_SPEED_M_PER_MIN
    
    @staticmethod
    def estimate_bus_duration(stops_count: int) -> int:
        """
        Estimate bus travel duration based on number of stops
        
        Args:
            stops_count: Number of stops to travel
        
        Returns:
            Estimated duration in minutes
        """
        MINUTES_PER_STOP = 3
        return stops_count * MINUTES_PER_STOP


# Create service instance
distance_service = DistanceService()