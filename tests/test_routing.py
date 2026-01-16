"""
Test routing service
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.routing_service import routing_service

def test_direct_routes():
    """Test direct route finding with known coordinates"""
    
    print("=" * 70)
    print("TESTING DIRECT ROUTE FINDER")
    print("=" * 70)
    
    # Test Case 1: PÉPINIÉRE → RELAIS BORJ EL AMRI (should use aller)
    print("\n🧪 Test Case 1: Valid Forward Route")
    print("From: PÉPINIÉRE area (36.7927, 10.0944)")
    print("To: RELAIS BORJ EL AMRI area (36.7181, 9.8944)")
    
    routes = routing_service.find_direct_routes(
        36.7927, 10.0944,  # Near PÉPINIÉRE
        36.7181, 9.8944    # Near RELAIS BORJ EL AMRI
    )
    
    print(f"\n📊 Found {len(routes)} route options:")
    for route in routes:
        status = "✅ VALID" if route['valid'] else "❌ INVALID"
        print(f"\n{status} - Bus {route['bus_line']} ({route['direction']})")
        print(f"  Board at: {route['start_stop']['name']} (#{route['start_stop']['number']})")
        print(f"  Exit at: {route['end_stop']['name']} (#{route['end_stop']['number']})")
        if route['valid']:
            print(f"  Stops: {route['validation']['stops_count']}")
            print(f"  Total time: {route['total_time_minutes']} minutes")
        else:
            print(f"  Reason: {route['validation']['reason']}")
    
    # Test Case 2: Reverse direction (should use retour)
    print("\n" + "=" * 70)
    print("🧪 Test Case 2: Reverse Direction")
    print("From: RELAIS BORJ EL AMRI area")
    print("To: PÉPINIÉRE area")
    
    routes = routing_service.find_direct_routes(
        36.7181, 9.8944,   # Near RELAIS BORJ EL AMRI
        36.7927, 10.0944   # Near PÉPINIÉRE
    )
    
    print(f"\n📊 Found {len(routes)} route options:")
    for route in routes:
        status = "✅ VALID" if route['valid'] else "❌ INVALID"
        print(f"\n{status} - Bus {route['bus_line']} ({route['direction']})")
        print(f"  Board at: {route['start_stop']['name']} (#{route['start_stop']['number']})")
        print(f"  Exit at: {route['end_stop']['name']} (#{route['end_stop']['number']})")
        if route['valid']:
            print(f"  Stops: {route['validation']['stops_count']}")
            print(f"  Total time: {route['total_time_minutes']} minutes")
    
    print("\n" + "=" * 70)
    print("✅ TESTS COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    test_direct_routes()