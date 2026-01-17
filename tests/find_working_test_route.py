#!/usr/bin/env python3
"""
Find a REAL working test route - starting AWAY from Tunis Marine
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.distance_service import distance_service
from app.utils.data_loader import data_loader

def main():
    print("\n" + "=" * 70)
    print("  FINDING A REAL TEST ROUTE")
    print("=" * 70)
    
    bus_data = data_loader.load_bus_data()
    
    # Tunis Marine coordinates
    tunis_marine = (36.8008, 10.1865)
    
    # Find buses that END near Tunis Marine (retour directions usually)
    print("\n  Step 1: Finding buses that END near Tunis Marine...")
    
    buses_ending_at_tunis = []
    for route in bus_data['routes']:
        last_stop = route['stops'][-1]
        dist = distance_service.haversine_distance(
            tunis_marine[0], tunis_marine[1],
            last_stop['latitude'], last_stop['longitude']
        )
        if dist <= 500:
            first_stop = route['stops'][0]
            buses_ending_at_tunis.append({
                'bus': route['bus_name'],
                'direction': route['direction'],
                'route': route,
                'first_stop': first_stop,
                'last_stop': last_stop,
                'total_stops': len(route['stops'])
            })
    
    print(f"  Found {len(buses_ending_at_tunis)} buses ending near Tunis Marine\n")
    
    for b in buses_ending_at_tunis[:5]:
        print(f"    Bus {b['bus']} ({b['direction']}): {b['first_stop']['stop_name']} → {b['last_stop']['stop_name']}")
    
    # Step 2: For each bus ending at Tunis, find what OTHER buses intersect with it
    print("\n" + "-" * 70)
    print("  Step 2: Finding transfer connections...")
    print("-" * 70)
    
    valid_transfers = []
    
    for tunis_bus in buses_ending_at_tunis[:10]:  # Check first 10
        route_to_tunis = tunis_bus['route']
        
        # Check stops on this route (not the first few - need room to board)
        for stop_idx, stop in enumerate(route_to_tunis['stops']):
            if stop['stop_number'] < 3:  # Need some stops ahead
                continue
            
            stops_to_tunis = tunis_bus['total_stops'] - stop['stop_number']
            if stops_to_tunis < 3:  # Need enough stops to reach Tunis
                continue
            
            # Find other buses at this stop
            for other_route in bus_data['routes']:
                if other_route['bus_name'] == route_to_tunis['bus_name']:
                    continue
                
                for other_stop in other_route['stops']:
                    dist = distance_service.haversine_distance(
                        stop['latitude'], stop['longitude'],
                        other_stop['latitude'], other_stop['longitude']
                    )
                    
                    if dist <= 400:  # Within walking distance
                        # Check: can we board the OTHER bus and ride to this transfer point?
                        stops_on_other = other_stop['stop_number']
                        if stops_on_other >= 5:  # At least 5 stops ridden
                            # This is a valid transfer!
                            other_first = other_route['stops'][0]
                            
                            # Make sure start is far from Tunis Marine
                            dist_from_tunis = distance_service.haversine_distance(
                                tunis_marine[0], tunis_marine[1],
                                other_first['latitude'], other_first['longitude']
                            )
                            
                            if dist_from_tunis > 2000:  # At least 2km from Tunis Marine
                                valid_transfers.append({
                                    'start_bus': other_route['bus_name'],
                                    'start_dir': other_route['direction'],
                                    'start_stop': other_first['stop_name'],
                                    'start_coords': (other_first['latitude'], other_first['longitude']),
                                    'transfer_stop_A': other_stop['stop_name'],
                                    'transfer_stop_B': stop['stop_name'],
                                    'walk_dist': dist,
                                    'end_bus': route_to_tunis['bus_name'],
                                    'end_dir': route_to_tunis['direction'],
                                    'stops_to_tunis': stops_to_tunis,
                                    'dist_from_tunis': dist_from_tunis
                                })
                        break
    
    # Remove duplicates and sort by distance from Tunis
    seen = set()
    unique = []
    for t in valid_transfers:
        key = t['start_bus'] + t['start_dir']
        if key not in seen:
            seen.add(key)
            unique.append(t)
    
    unique.sort(key=lambda x: -x['dist_from_tunis'])
    
    print(f"\n  Found {len(unique)} valid transfer routes!\n")
    
    for t in unique[:10]:
        print(f"    From: {t['start_stop']} (Bus {t['start_bus']} {t['start_dir']})")
        print(f"      → Transfer at {t['transfer_stop_A']} → Bus {t['end_bus']} → Tunis Marine")
        print(f"      Distance from Tunis: {t['dist_from_tunis']/1000:.1f} km")
        print()
    
    # Suggest best test
    if unique:
        best = unique[0]
        print("\n" + "=" * 70)
        print("  RECOMMENDED TEST")
        print("=" * 70)
        print(f"""
  Route: Bus {best['start_bus']} ({best['start_dir']}) → Bus {best['end_bus']} → TUNIS MARINE
  
  START: {best['start_stop']}
    Coordinates: {best['start_coords']}
    Distance from Tunis Marine: {best['dist_from_tunis']/1000:.1f} km
  
  Transfer at: {best['transfer_stop_A']} (walk {best['walk_dist']:.0f}m)
  
  END: TUNIS MARINE
    Coordinates: (36.8008, 10.1865)
  
  ═══════════════════════════════════════════════════════════════════════
  
  TEST WITH quick_test_transfer.py:
  
  Edit the test file and change start/end to:
    start = ({best['start_coords'][0]}, {best['start_coords'][1]})
    end = (36.8008, 10.1865)
  
  OR use curl:
  
  curl -X POST http://localhost:5000/api/routes/transfer \\
    -H "Content-Type: application/json" \\
    -d '{{
      "start": {{"latitude": {best['start_coords'][0]}, "longitude": {best['start_coords'][1]}}},
      "end": {{"latitude": 36.8008, "longitude": 10.1865}},
      "max_results": 5
    }}'
""")

if __name__ == "__main__":
    main()