import pandas as pd
import json

# PART 1: CONVERT EXCEL TO JSON

print("=" * 70)
print("TRANSTU DATA CONVERSION & VERIFICATION")
print("=" * 70)

# Path to your Excel file
file_path = r"C:\Users\HP\Desktop\TransTu data\Bus\lignes-bus.xlsx"

# Read the Excel file
df = pd.read_excel(file_path)

print("\n[1] Excel Data Loaded")
print(f"    Total rows in Excel: {len(df)}")

# Dictionary to store all bus routes
bus_routes = {}

# Process each row
for index, row in df.iterrows():
    bus_line = str(row['N° de la ligne']).strip()
    
    # FIX: Normalize naming inconsistencies
    # Convert "X Retour" or "X RETOUR" to "X (Retour)"
    if bus_line.endswith(' Retour') and '(Retour)' not in bus_line:
        bus_line = bus_line.replace(' Retour', ' (Retour)')
    if bus_line.endswith(' RETOUR') and '(Retour)' not in bus_line:
        bus_line = bus_line.replace(' RETOUR', ' (Retour)')
    if bus_line.endswith(' retour') and '(Retour)' not in bus_line:
        bus_line = bus_line.replace(' retour', ' (Retour)')
    
    stop_number = int(row['N° de station'])
    stop_name = str(row['Nom de station']).strip()
    longitude = float(row['Longitude'])
    latitude = float(row['Latitude'])
    
    # Determine direction and create route ID
    if '(Retour)' in bus_line or '(retour)' in bus_line:
        bus_name = bus_line.replace('(Retour)', '').replace('(retour)', '').strip()
        direction = 'retour'
        route_id = f"bus_{bus_name}_retour"
    else:
        bus_name = bus_line
        direction = 'aller'
        route_id = f"bus_{bus_name}_aller"
    
    # Create route entry if it doesn't exist
    if route_id not in bus_routes:
        bus_routes[route_id] = {
            'id': route_id,
            'bus_name': bus_name,
            'type': 'bus',
            'direction': direction,
            'stops': []
        }
    
    # Add stop to route
    stop_data = {
        'stop_number': stop_number,
        'stop_name': stop_name,
        'longitude': longitude,
        'latitude': latitude
    }
    
    bus_routes[route_id]['stops'].append(stop_data)

# Convert to list
bus_routes_list = list(bus_routes.values())

# Create final JSON structure
output_data = {
    'type': 'bus',
    'routes': bus_routes_list,
    'metadata': {
        'total_routes': len(bus_routes_list),
        'total_stops': sum(len(route['stops']) for route in bus_routes_list),
        'source': 'lignes-bus.xlsx'
    }
}

# Save to JSON file
output_path = r"C:\Users\HP\Desktop\TransTu data\Bus\bus_routes.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"[2] Conversion complete - Saved to: {output_path}")

# PART 2: CALCULATE DETAILED STATISTICS

print("\n" + "=" * 70)
print("DETAILED STATISTICS")
print("=" * 70)

# Count unique bus lines (without direction)
unique_lines = set()
aller_count = 0
retour_count = 0

for route in bus_routes_list:
    unique_lines.add(route['bus_name'])
    if route['direction'] == 'aller':
        aller_count += 1
    else:
        retour_count += 1

# Count unique physical stops (by coordinates)
unique_stops = set()
for route in bus_routes_list:
    for stop in route['stops']:
        # Use coordinates to identify unique stops
        stop_key = (stop['latitude'], stop['longitude'])
        unique_stops.add(stop_key)

# Count unique stop names
unique_stop_names = set()
for route in bus_routes_list:
    for stop in route['stops']:
        unique_stop_names.add(stop['stop_name'])

# Calculate average stops per route
total_stop_records = sum(len(route['stops']) for route in bus_routes_list)
avg_stops_per_route = total_stop_records / len(bus_routes_list) if bus_routes_list else 0

# Find coordinate bounds
all_lats = []
all_lons = []
for route in bus_routes_list:
    for stop in route['stops']:
        all_lats.append(stop['latitude'])
        all_lons.append(stop['longitude'])

min_lat = min(all_lats)
max_lat = max(all_lats)
min_lon = min(all_lons)
max_lon = max(all_lons)

print("\n📊 ROUTE STATISTICS:")
print(f"    Unique Bus Lines: {len(unique_lines)}")
print(f"    Total Directional Routes: {len(bus_routes_list)}")
print(f"      - Aller (outbound): {aller_count}")
print(f"      - Retour (return): {retour_count}")

print("\n STOP STATISTICS:")
print(f"    Unique Physical Stops (by coordinates): {len(unique_stops)}")
print(f"    Unique Stop Names: {len(unique_stop_names)}")
print(f"    Total Stop Records: {total_stop_records}")
print(f"    Average Stops per Route: {avg_stops_per_route:.1f}")

print("\n  GEOGRAPHIC COVERAGE:")
print(f"    Latitude Range: {min_lat:.6f} to {max_lat:.6f}")
print(f"    Longitude Range: {min_lon:.6f} to {max_lon:.6f}")

# Check if all buses have return routes
lines_with_retour = set()
lines_with_aller = set()
for route in bus_routes_list:
    if route['direction'] == 'aller':
        lines_with_aller.add(route['bus_name'])
    else:
        lines_with_retour.add(route['bus_name'])

lines_with_both = lines_with_aller & lines_with_retour
lines_only_aller = lines_with_aller - lines_with_retour
lines_only_retour = lines_with_retour - lines_with_aller

print("\n DIRECTION COVERAGE:")
print(f"    Lines with BOTH directions: {len(lines_with_both)}")
print(f"    Lines with ONLY aller: {len(lines_only_aller)}")
print(f"    Lines with ONLY retour: {len(lines_only_retour)}")

if lines_only_aller:
    print(f"   Lines without retour: {', '.join(sorted(lines_only_aller))}")
if lines_only_retour:
    print(f"   Lines without aller: {', '.join(sorted(lines_only_retour))}")

# PART 3: GENERATE REPORT TABLE

print("\n" + "=" * 70)
print("SUMMARY FOR TECHNICAL REPORT")
print("=" * 70)

print("""
### 2.4.1 Dataset Summary

| Metric | Value |
|--------|-------|
| Total Bus Lines | {unique_lines} |
| Directional Routes (aller + retour) | {total_routes} |
| Routes - Aller (outbound) | {aller} |
| Routes - Retour (return) | {retour} |
| Unique Physical Stops | {unique_stops} |
| Total Stop Records | {total_records} |
| Average Stops per Route | {avg_stops} |
| Geographic Coverage | Greater Tunis (4 governorates) |
| Coordinate System | WGS84 (EPSG:4326) |
| Latitude Range | {min_lat:.4f}° to {max_lat:.4f}° |
| Longitude Range | {min_lon:.4f}° to {max_lon:.4f}° |
| Data Source Authority | Ministère des Transports Tunisien |
""".format(
    unique_lines=len(unique_lines),
    total_routes=len(bus_routes_list),
    aller=aller_count,
    retour=retour_count,
    unique_stops=len(unique_stops),
    total_records=total_stop_records,
    avg_stops=f"{avg_stops_per_route:.1f}",
    min_lat=min_lat,
    max_lat=max_lat,
    min_lon=min_lon,
    max_lon=max_lon
))

# PART 4: DATA QUALITY CHECKS

print("\n" + "=" * 70)
print("DATA QUALITY CHECKS")
print("=" * 70)

# Check for missing data
missing_checks = {
    'Routes with no stops': sum(1 for r in bus_routes_list if len(r['stops']) == 0),
    'Stops with invalid coordinates': 0,
    'Duplicate stop names': len(unique_stop_names) < total_stop_records
}

# Check coordinate validity (Expanded Greater Tunis bounds to include peripheral areas)
TUNIS_MIN_LAT = 36.50
TUNIS_MAX_LAT = 37.10
TUNIS_MIN_LON = 9.60
TUNIS_MAX_LON = 10.40

invalid_coords = 0
for route in bus_routes_list:
    for stop in route['stops']:
        if not (TUNIS_MIN_LAT <= stop['latitude'] <= TUNIS_MAX_LAT and
                TUNIS_MIN_LON <= stop['longitude'] <= TUNIS_MAX_LON):
            invalid_coords += 1

print(f"\n Routes with stops: {len(bus_routes_list) - missing_checks['Routes with no stops']}/{len(bus_routes_list)}")
print(f" Valid coordinates: {total_stop_records - invalid_coords}/{total_stop_records}")

if invalid_coords > 0:
    print(f" WARNING: {invalid_coords} stops have coordinates outside Greater Tunis bounds")

# PART 5: SAMPLE DATA
print("\n" + "=" * 70)
print("SAMPLE DATA")
print("=" * 70)

if bus_routes_list:
    print("\n First Route Example:")
    first_route = bus_routes_list[0]
    print(f"    ID: {first_route['id']}")
    print(f"    Bus: {first_route['bus_name']}")
    print(f"    Direction: {first_route['direction']}")
    print(f"    Number of stops: {len(first_route['stops'])}")
    print(f"    First stop: {first_route['stops'][0]['stop_name']}")
    print(f"    Last stop: {first_route['stops'][-1]['stop_name']}")

print("\n" + "=" * 70)
print(" VERIFICATION COMPLETE!")
print("=" * 70)