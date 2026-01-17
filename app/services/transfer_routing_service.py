"""
Transfer Routing Service - Find routes with one transfer
FIXED VERSION v2: Properly filters out wrong-direction routes
"""
from typing import List, Dict, Optional
from app.services.distance_service import distance_service
from app.utils.data_loader import data_loader

class TransferRoutingService:
    """Find routes requiring one transfer between two buses"""
    
    def __init__(self, max_walking_distance: int = 500):
        self.max_walking_distance = max_walking_distance
        self.bus_data = data_loader.load_bus_data()
    
    def find_transfer_routes(self, start_lat: float, start_lon: float,
                            end_lat: float, end_lon: float,
                            max_results: int = 10) -> List[Dict]:
        """
        Find routes requiring one transfer between two buses
        """
        results = []
        checked_combinations = set()
        
        # STEP 1: Find all buses with stops near START location
        # This now returns ONLY buses where we can travel forward
        buses_near_start = self._find_buses_near_location_for_boarding(start_lat, start_lon)
        
        if not buses_near_start:
            print("No buses found near start location with forward travel possible")
            return []
        
        print(f"Found {len(buses_near_start)} usable buses near start location")
        
        # STEP 2: For each bus near START
        for bus_A_info in buses_near_start:
            bus_A = bus_A_info['route']
            boarding_stop_A = bus_A_info['nearest_stop']
            
            print(f"  Checking Bus {bus_A['bus_name']} ({bus_A['direction']}) from stop #{boarding_stop_A['stop_number']} ({bus_A_info['stops_ahead']} stops ahead)")
            
            # STEP 3: Find all potential transfer points on bus_A
            transfer_points_checked = 0
            for stop_A in bus_A['stops']:
                if stop_A['stop_number'] <= boarding_stop_A['stop_number']:
                    continue
                
                transfer_points_checked += 1
                
                # STEP 4: Find buses near this potential transfer stop
                buses_near_transfer = self._find_buses_near_location_for_boarding(
                    stop_A['latitude'], 
                    stop_A['longitude']
                )
                
                # STEP 5: For each bus at transfer point
                for bus_B_info in buses_near_transfer:
                    bus_B = bus_B_info['route']
                    boarding_stop_B = bus_B_info['nearest_stop']
                    
                    # Skip if same bus line (including variants like 23 and 23E)
                    # Extract base bus number for comparison
                    base_A = ''.join(c for c in bus_A['bus_name'] if c.isdigit())
                    base_B = ''.join(c for c in bus_B['bus_name'] if c.isdigit())
                    if bus_A['bus_name'] == bus_B['bus_name']:
                        continue
                    
                    combination_key = (
                        bus_A['id'], 
                        stop_A['stop_number'],
                        bus_B['id'],
                        boarding_stop_B['stop_number']
                    )
                    
                    if combination_key in checked_combinations:
                        continue
                    
                    checked_combinations.add(combination_key)
                    
                    # STEP 6: Check if this bus can reach destination
                    for stop_B in bus_B['stops']:
                        if stop_B['stop_number'] <= boarding_stop_B['stop_number']:
                            continue
                        
                        distance_to_dest = distance_service.haversine_distance(
                            stop_B['latitude'], stop_B['longitude'],
                            end_lat, end_lon
                        )
                        
                        if distance_to_dest <= self.max_walking_distance:
                            route_details = self._build_transfer_route(
                                start_lat, start_lon,
                                bus_A, boarding_stop_A, stop_A,
                                bus_B, boarding_stop_B, stop_B,
                                end_lat, end_lon,
                                distance_to_dest
                            )
                            
                            if route_details['valid']:
                                results.append(route_details)
                                print(f"    ✓ Found route: {bus_A['bus_name']} → {bus_B['bus_name']}")
                                
                                if len(results) >= max_results * 5:
                                    break
                        
                        # Don't check too many stops ahead
                        if stop_B['stop_number'] - boarding_stop_B['stop_number'] > 20:
                            break
                
                if len(results) >= max_results * 5:
                    break
            
            if len(results) >= max_results * 5:
                break
        
        print(f"Found {len(results)} valid transfer routes")
        
        results.sort(key=lambda x: x['total_time_minutes'])
        return results[:max_results]
    
    def _find_buses_near_location_for_boarding(self, lat: float, lon: float, 
                                                min_stops_ahead: int = 5) -> List[Dict]:
        """
        Find buses where we can board and travel FORWARD for at least min_stops_ahead stops.
        This filters out buses where we'd be boarding near the end of the line.
        """
        nearby_buses = []
        
        for route in self.bus_data['routes']:
            total_stops = len(route['stops'])
            
            # Find the nearest stop on this route
            best_stop = None
            min_distance = float('inf')
            
            for stop in route['stops']:
                distance = distance_service.haversine_distance(
                    lat, lon,
                    stop['latitude'], stop['longitude']
                )
                
                if distance <= self.max_walking_distance:
                    stops_ahead = total_stops - stop['stop_number']
                    
                    # Only consider this stop if there are enough stops ahead
                    if stops_ahead >= min_stops_ahead:
                        if distance < min_distance:
                            min_distance = distance
                            best_stop = {
                                **stop, 
                                'distance': round(distance),
                                'stops_ahead': stops_ahead
                            }
            
            if best_stop:
                nearby_buses.append({
                    'route': route,
                    'nearest_stop': best_stop,
                    'stops_ahead': best_stop['stops_ahead']
                })
        
        # Sort by: most stops ahead first, then by walking distance
        nearby_buses.sort(key=lambda x: (-x['stops_ahead'], x['nearest_stop']['distance']))
        
        return nearby_buses
    
    def _find_buses_near_location(self, lat: float, lon: float) -> List[Dict]:
        """
        Find all buses with stops within walking distance (legacy method).
        Used for finding destination stops.
        """
        nearby_buses = []
        
        for route in self.bus_data['routes']:
            nearest_stop = None
            min_distance = float('inf')
            
            for stop in route['stops']:
                distance = distance_service.haversine_distance(
                    lat, lon,
                    stop['latitude'], stop['longitude']
                )
                
                if distance < min_distance and distance <= self.max_walking_distance:
                    min_distance = distance
                    nearest_stop = {**stop, 'distance': round(distance)}
            
            if nearest_stop:
                nearby_buses.append({
                    'route': route,
                    'nearest_stop': nearest_stop
                })
        
        return nearby_buses
    
    def _build_transfer_route(self, start_lat: float, start_lon: float,
                             bus_A: Dict, boarding_A: Dict, transfer_A: Dict,
                             bus_B: Dict, boarding_B: Dict, alighting_B: Dict,
                             end_lat: float, end_lon: float,
                             walk_to_end: float) -> Dict:
        """Build complete transfer route details with timing"""
        
        transfer_distance = distance_service.haversine_distance(
            transfer_A['latitude'], transfer_A['longitude'],
            boarding_B['latitude'], boarding_B['longitude']
        )
        
        if transfer_distance > self.max_walking_distance:
            return {'valid': False, 'reason': 'Transfer distance too far'}
        
        walk_to_start = boarding_A['distance']
        
        walk_time_start = round(distance_service.calculate_walking_time(walk_to_start))
        
        stops_on_A = transfer_A['stop_number'] - boarding_A['stop_number']
        bus_time_A = distance_service.estimate_bus_duration(stops_on_A)
        
        transfer_walk_time = round(distance_service.calculate_walking_time(transfer_distance))
        
        stops_on_B = alighting_B['stop_number'] - boarding_B['stop_number']
        bus_time_B = distance_service.estimate_bus_duration(stops_on_B)
        
        walk_time_end = round(distance_service.calculate_walking_time(walk_to_end))
        
        total_time = (walk_time_start + bus_time_A + transfer_walk_time + 
                     bus_time_B + walk_time_end)
        
        return {
            'valid': True,
            'type': 'transfer',
            'total_time_minutes': total_time,
            'summary': {
                'description': f'Take Bus {bus_A["bus_name"]}, transfer to Bus {bus_B["bus_name"]}',
                'total_walking_meters': round(walk_to_start + transfer_distance + walk_to_end),
                'total_bus_stops': stops_on_A + stops_on_B,
                'total_transfers': 1,
                'buses_used': [bus_A['bus_name'], bus_B['bus_name']]
            },
            'segments': [
                {
                    'step': 1,
                    'type': 'walk',
                    'instruction': f'Walk to {boarding_A["stop_name"]}',
                    'distance_meters': walk_to_start,
                    'duration_minutes': walk_time_start,
                    'details': {
                        'to_stop': boarding_A['stop_name'],
                        'coordinates': {
                            'latitude': boarding_A['latitude'],
                            'longitude': boarding_A['longitude']
                        }
                    }
                },
                {
                    'step': 2,
                    'type': 'bus',
                    'instruction': f'Take Bus {bus_A["bus_name"]} ({bus_A["direction"]})',
                    'bus_line': bus_A['bus_name'],
                    'direction': bus_A['direction'],
                    'board_at': {
                        'name': boarding_A['stop_name'],
                        'number': boarding_A['stop_number'],
                        'coordinates': {
                            'latitude': boarding_A['latitude'],
                            'longitude': boarding_A['longitude']
                        }
                    },
                    'alight_at': {
                        'name': transfer_A['stop_name'],
                        'number': transfer_A['stop_number'],
                        'coordinates': {
                            'latitude': transfer_A['latitude'],
                            'longitude': transfer_A['longitude']
                        }
                    },
                    'stops_count': stops_on_A,
                    'duration_minutes': bus_time_A
                },
                {
                    'step': 3,
                    'type': 'walk',
                    'instruction': f'Walk to {boarding_B["stop_name"]} for transfer',
                    'distance_meters': round(transfer_distance),
                    'duration_minutes': transfer_walk_time,
                    'details': {
                        'from_stop': transfer_A['stop_name'],
                        'to_stop': boarding_B['stop_name'],
                        'is_transfer': True
                    }
                },
                {
                    'step': 4,
                    'type': 'bus',
                    'instruction': f'Take Bus {bus_B["bus_name"]} ({bus_B["direction"]})',
                    'bus_line': bus_B['bus_name'],
                    'direction': bus_B['direction'],
                    'board_at': {
                        'name': boarding_B['stop_name'],
                        'number': boarding_B['stop_number'],
                        'coordinates': {
                            'latitude': boarding_B['latitude'],
                            'longitude': boarding_B['longitude']
                        }
                    },
                    'alight_at': {
                        'name': alighting_B['stop_name'],
                        'number': alighting_B['stop_number'],
                        'coordinates': {
                            'latitude': alighting_B['latitude'],
                            'longitude': alighting_B['longitude']
                        }
                    },
                    'stops_count': stops_on_B,
                    'duration_minutes': bus_time_B
                },
                {
                    'step': 5,
                    'type': 'walk',
                    'instruction': 'Walk to destination',
                    'distance_meters': round(walk_to_end),
                    'duration_minutes': walk_time_end,
                    'details': {
                        'from_stop': alighting_B['stop_name'],
                        'to_destination': True
                    }
                }
            ]
        }


# Create service instance
transfer_routing_service = TransferRoutingService()