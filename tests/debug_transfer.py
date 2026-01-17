#!/usr/bin/env python3
"""
DEBUG: Why can't we connect to TUNIS MARINE?
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.distance_service import distance_service
from app.utils.data_loader import data_loader

def main():
    print("\n" + "=" * 70)
    print("  DEBUG: Finding connection to TUNIS MARINE")
    print("=" * 70)
    
    bus_data = data_loader.load_bus_data()
    
    # Destination: TUNIS MARINE
    end_lat, end_lon = 36.8008, 10.1865
    
    # Step 1: What buses have stops near TUNIS MARINE?
    print(f"\n  STEP 1: Buses with stops near TUNIS MARINE ({end_lat}, {end_lon})")
    print("-" * 70)
    
    buses_at_end = []
    for route in bus_data['routes']:
        for stop in route['stops']:
            dist = distance_service.haversine_distance(
                end_lat, end_lon,
                stop['latitude'], stop['longitude']
            )
            if dist <= 500:
                buses_at_end.append({
                    'bus': route['bus_name'],
                    'direction': route['direction'],
                    'stop': stop['stop_name'],
                    'stop_num': stop['stop_number'],
                    'total_stops': len(route['stops']),
                    'distance': dist
                })
                break
    
    print(f"\n  Found {len(buses_at_end)} buses near TUNIS MARINE:\n")
    for b in buses_at_end[:15]:
        print(f"    Bus {b['bus']} ({b['direction']})")
        print(f"      Stop: {b['stop']} (#{b['stop_num']} of {b['total_stops']})")
        print(f"      Distance to destination: {b['distance']:.0f}m")
    
    if len(buses_at_end) > 15:
        print(f"\n    ... and {len(buses_at_end) - 15} more")
    
    # Step 2: Where does Bus 23 retour go? Does it pass near any of these?
    print("\n" + "-" * 70)
    print("  STEP 2: Where does Bus 23 (retour) go?")
    print("-" * 70)
    
    bus23_retour = None
    for route in bus_data['routes']:
        if route['bus_name'] == '23' and route['direction'] == 'retour':
            bus23_retour = route
            break
    
    if bus23_retour:
        print(f"\n  Bus 23 (retour) has {len(bus23_retour['stops'])} stops:")
        print(f"    FROM: {bus23_retour['stops'][0]['stop_name']}")
        print(f"    TO:   {bus23_retour['stops'][-1]['stop_name']}")
        
        # Show key stops
        print(f"\n  Key stops on Bus 23 retour:")
        for stop in bus23_retour['stops'][::5]:  # Every 5th stop
            print(f"    #{stop['stop_number']}: {stop['stop_name']}")
        
        # Check last stop
        last = bus23_retour['stops'][-1]
        print(f"\n  FINAL STOP: {last['stop_name']}")
        print(f"    Coordinates: ({last['latitude']}, {last['longitude']})")
        
        # Distance from last stop to TUNIS MARINE
        dist_to_end = distance_service.haversine_distance(
            last['latitude'], last['longitude'],
            end_lat, end_lon
        )
        print(f"    Distance to TUNIS MARINE: {dist_to_end:.0f}m")
        
        if dist_to_end > 500:
            print(f"     TOO FAR! Bus 23 doesn't go to Tunis Marine directly!")
    
    # Step 3: Find where Bus 23 retour intersects with buses that go to Tunis Marine
    print("\n" + "-" * 70)
    print("  STEP 3: Where can you transfer from Bus 23 to reach TUNIS MARINE?")
    print("-" * 70)
    
    # Get bus names that reach Tunis Marine
    buses_reaching_end = set(b['bus'] for b in buses_at_end)
    print(f"\n  Buses that reach TUNIS MARINE: {buses_reaching_end}")
    
    # Check each stop on Bus 23 retour for intersection
    if bus23_retour:
        print(f"\n  Checking each stop on Bus 23 retour for transfer options...")
        
        transfer_points = []
        for stop in bus23_retour['stops']:
            # Skip first few stops (too early to transfer)
            if stop['stop_number'] < 3:
                continue
            
            # Find buses at this stop
            for route in bus_data['routes']:
                if route['bus_name'] in buses_reaching_end:
                    for other_stop in route['stops']:
                        dist = distance_service.haversine_distance(
                            stop['latitude'], stop['longitude'],
                            other_stop['latitude'], other_stop['longitude']
                        )
                        if dist <= 500:
                            # Check if this stop has enough stops ahead to reach destination
                            stops_ahead = len(route['stops']) - other_stop['stop_number']
                            if stops_ahead >= 3:
                                transfer_points.append({
                                    'bus23_stop': stop['stop_name'],
                                    'bus23_num': stop['stop_number'],
                                    'transfer_to': route['bus_name'],
                                    'transfer_dir': route['direction'],
                                    'transfer_stop': other_stop['stop_name'],
                                    'transfer_num': other_stop['stop_number'],
                                    'walk_dist': dist,
                                    'stops_ahead': stops_ahead
                                })
                            break
        
        if transfer_points:
            print(f"\n  Found {len(transfer_points)} potential transfer points:\n")
            seen = set()
            for tp in transfer_points[:20]:
                key = (tp['bus23_stop'], tp['transfer_to'])
                if key in seen:
                    continue
                seen.add(key)
                print(f"    At {tp['bus23_stop']} (Bus 23 stop #{tp['bus23_num']}):")
                print(f"      → Transfer to Bus {tp['transfer_to']} ({tp['transfer_dir']})")
                print(f"        Walk {tp['walk_dist']:.0f}m to {tp['transfer_stop']}")
                print(f"        Then {tp['stops_ahead']} stops ahead to destination")
        else:
            print("\n   NO TRANSFER POINTS FOUND!")
            print("  Bus 23 retour doesn't intersect with any bus going to TUNIS MARINE")
            print("\n  This route may require 2+ transfers or isn't possible with current data")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()