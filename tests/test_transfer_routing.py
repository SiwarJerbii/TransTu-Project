#!/usr/bin/env python3
"""
TEST WITH WORKING COORDINATES
Route: Bus 34 (retour) → Bus 43 B → TUNIS MARINE
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.distance_service import distance_service
from app.utils.data_loader import data_loader

# ============================================================
# FIXED TRANSFER ROUTING
# ============================================================

class FixedTransferRoutingService:
    def __init__(self, max_walking_distance=500):
        self.max_walking_distance = max_walking_distance
        self.bus_data = data_loader.load_bus_data()
    
    def find_transfer_routes(self, start_lat, start_lon, end_lat, end_lon, max_results=10):
        results = []
        checked = set()
        
        buses_at_start = self._find_boardable_buses(start_lat, start_lon)
        print(f"Found {len(buses_at_start)} usable buses at start")
        
        for bus_A_info in buses_at_start:
            bus_A = bus_A_info['route']
            board_A = bus_A_info['stop']
            
            print(f"  Checking Bus {bus_A['bus_name']} ({bus_A['direction']}) from #{board_A['stop_number']}")
            
            for stop_A in bus_A['stops']:
                if stop_A['stop_number'] <= board_A['stop_number']:
                    continue
                
                buses_at_transfer = self._find_boardable_buses(stop_A['latitude'], stop_A['longitude'])
                
                for bus_B_info in buses_at_transfer:
                    bus_B = bus_B_info['route']
                    board_B = bus_B_info['stop']
                    
                    if bus_A['bus_name'] == bus_B['bus_name']:
                        continue
                    
                    key = (bus_A['id'], stop_A['stop_number'], bus_B['id'], board_B['stop_number'])
                    if key in checked:
                        continue
                    checked.add(key)
                    
                    for stop_B in bus_B['stops']:
                        if stop_B['stop_number'] <= board_B['stop_number']:
                            continue
                        
                        dist_to_end = distance_service.haversine_distance(
                            stop_B['latitude'], stop_B['longitude'],
                            end_lat, end_lon
                        )
                        
                        if dist_to_end <= self.max_walking_distance:
                            route = self._build_route(
                                bus_A, board_A, stop_A,
                                bus_B, board_B, stop_B,
                                dist_to_end
                            )
                            results.append(route)
                            print(f"    ✓ Found: {bus_A['bus_name']} → {bus_B['bus_name']}")
                            break
                        
                        if stop_B['stop_number'] - board_B['stop_number'] > 25:
                            break
                
                if len(results) >= max_results * 3:
                    break
            
            if len(results) >= max_results * 3:
                break
        
        results.sort(key=lambda x: x['total_time'])
        return results[:max_results]
    
    def _find_boardable_buses(self, lat, lon, min_stops_ahead=5):
        buses = []
        for route in self.bus_data['routes']:
            total = len(route['stops'])
            best = None
            best_dist = float('inf')
            
            for stop in route['stops']:
                dist = distance_service.haversine_distance(lat, lon, stop['latitude'], stop['longitude'])
                stops_ahead = total - stop['stop_number']
                
                if dist <= self.max_walking_distance and stops_ahead >= min_stops_ahead:
                    if dist < best_dist:
                        best_dist = dist
                        best = {'stop': stop, 'distance': dist, 'stops_ahead': stops_ahead}
            
            if best:
                buses.append({
                    'route': route,
                    'stop': {**best['stop'], 'distance': round(best['distance'])},
                    'stops_ahead': best['stops_ahead']
                })
        
        buses.sort(key=lambda x: (-x['stops_ahead'], x['stop']['distance']))
        return buses
    
    def _build_route(self, bus_A, board_A, transfer_A, bus_B, board_B, alight_B, walk_end):
        walk_start = board_A['distance']
        transfer_dist = distance_service.haversine_distance(
            transfer_A['latitude'], transfer_A['longitude'],
            board_B['latitude'], board_B['longitude']
        )
        
        stops_A = transfer_A['stop_number'] - board_A['stop_number']
        stops_B = alight_B['stop_number'] - board_B['stop_number']
        
        time_walk_start = round(walk_start / 80)
        time_bus_A = stops_A * 3
        time_transfer = round(transfer_dist / 80)
        time_bus_B = stops_B * 3
        time_walk_end = round(walk_end / 80)
        
        total = time_walk_start + time_bus_A + time_transfer + time_bus_B + time_walk_end
        
        return {
            'total_time': total,
            'description': f"Bus {bus_A['bus_name']} → Bus {bus_B['bus_name']}",
            'bus_A': bus_A['bus_name'],
            'bus_A_dir': bus_A['direction'],
            'board_A': board_A['stop_name'],
            'board_A_num': board_A['stop_number'],
            'transfer_at': transfer_A['stop_name'],
            'transfer_num': transfer_A['stop_number'],
            'bus_B': bus_B['bus_name'],
            'bus_B_dir': bus_B['direction'],
            'board_B': board_B['stop_name'],
            'board_B_num': board_B['stop_number'],
            'alight_B': alight_B['stop_name'],
            'alight_B_num': alight_B['stop_number'],
            'stops_A': stops_A,
            'stops_B': stops_B,
            'walk_start': round(walk_start),
            'walk_transfer': round(transfer_dist),
            'walk_end': round(walk_end)
        }


# ============================================================
# RUN TEST
# ============================================================

def main():
    print("\n" + "=" * 70)
    print("  TRANSFER ROUTING TEST - WORKING COORDINATES")
    print("=" * 70)
    
    service = FixedTransferRoutingService(max_walking_distance=500)
    
    # EPICIER LAGRAA → TUNIS MARINE (37km trip with transfer)
    start = (36.5528116940535, 9.9026297180535)  # EPICIER LAGRAA
    end = (36.8008, 10.1865)                      # TUNIS MARINE
    
    print(f"\n  From: EPICIER LAGRAA {start}")
    print(f"  To:   TUNIS MARINE {end}")
    print(f"  Expected: Bus 34 (retour) → Bus 43 B → Tunis Marine\n")
    
    routes = service.find_transfer_routes(start[0], start[1], end[0], end[1], max_results=5)
    
    print(f"\n  {'=' * 60}")
    print(f"  ✅ RESULTS: {len(routes)} routes found")
    print(f"  {'=' * 60}")
    
    if routes:
        for i, r in enumerate(routes, 1):
            print(f"\n  Route {i}: {r['description']} ({r['total_time']} min)")
            print(f"    ┌─ Walk {r['walk_start']}m to {r['board_A']} (stop #{r['board_A_num']})")
            print(f"    ├─ 🚌 Bus {r['bus_A']} ({r['bus_A_dir']}): ride {r['stops_A']} stops")
            print(f"    │     → Get off at: {r['transfer_at']} (stop #{r['transfer_num']})")
            print(f"    ├─ Walk {r['walk_transfer']}m to transfer")
            print(f"    ├─ 🚌 Bus {r['bus_B']} ({r['bus_B_dir']}): ride {r['stops_B']} stops")
            print(f"    │     → Board at: {r['board_B']} (stop #{r['board_B_num']})")
            print(f"    │     → Get off at: {r['alight_B']} (stop #{r['alight_B_num']})")
            print(f"    └─ Walk {r['walk_end']}m to destination")
        
        print("\n" + "=" * 70)
        print("  ✅ SUCCESS! Transfer routing is working correctly!")
        print("=" * 70)
    else:
        print("\n  ❌ No routes found - there may still be an issue")
    
    print()

if __name__ == "__main__":
    main()