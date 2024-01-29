import math

# Generated with GPT3.5
def move_coordinates(lat, lon, distance_feet, bearing_degrees):
    # Earth radius in feet (mean radius)
    earth_radius_feet = 20902231.93  # feet

    # Convert distance from feet to radians
    distance_radians = distance_feet / earth_radius_feet

    # Convert bearing from degrees to radians
    bearing_radians = math.radians(bearing_degrees)

    # Convert current latitude and longitude to radians
    lat_radians = math.radians(lat)
    lon_radians = math.radians(lon)

    # Calculate new latitude
    new_lat_radians = math.asin(math.sin(lat_radians) * math.cos(distance_radians) +
                                math.cos(lat_radians) * math.sin(distance_radians) * math.cos(bearing_radians))

    # Calculate new longitude
    new_lon_radians = lon_radians + math.atan2(math.sin(bearing_radians) * math.sin(distance_radians) * math.cos(lat_radians),
                                               math.cos(distance_radians) - math.sin(lat_radians) * math.sin(new_lat_radians))

    # Convert new latitude and longitude to degrees
    new_lat = math.degrees(new_lat_radians)
    new_lon = math.degrees(new_lon_radians)

    return new_lat, new_lon

# Generated with gpt 3.5
def haversine_distance_feet(lat1, lon1, lat2, lon2):
    # Earth radius in feet (mean radius)
    earth_radius_feet = 20902231.93  # feet

    # Convert latitude and longitude from degrees to radians
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    # Calculate differences
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Calculate distance in feet
    distance_feet = earth_radius_feet * c

    return distance_feet

# Generated with gpt3.5
def haversine_distance_and_components(lat1, lon1, lat2, lon2):
    # Earth radius in feet (mean radius)
    earth_radius_feet = 20902231.93  # feet

    # Convert latitude and longitude from degrees to radians
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    # Calculate differences
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Calculate distance in feet
    distance_feet = earth_radius_feet * c

    # Calculate horizontal and vertical components
    horizontal_component = distance_feet * math.cos(delta_lat)
    vertical_component = distance_feet * math.sin(delta_lat)

    return distance_feet, horizontal_component, vertical_component

def mock_folium_map(coords=None):

    return [
        {
            # These two will never change... coords of initial click on map
            'latitude': 41.8781,
            'longitude': -87.6298,
            # Will be modified and plotted
            'modified_latitude': 41.8781,
            'modified_longitude': -87.6198,
            'name': "Main St",
            'fontsize': 12,
            'angle': 0,
        },
        {
            # These two will never change... coords of initial click on map
            'latitude': 41.8741,
            'longitude': -87.6298,
            # Will be modified and plotted
            'modified_latitude': 41.8381,
            'modified_longitude': -87.6298,
            'name': "State St",
            'fontsize': 12,
            'angle': 0,
        },
        {
            # These two will never change... coords of initial click on map
            'latitude': 41.8781,
            'longitude': -87.6278,
            # Will be modified and plotted
            'modified_latitude': 41.8781,
            'modified_longitude': -87.6298,
            'name': "1st st",
            'fontsize': 12,
            'angle': 0,
        },
    ]

if __name__ == '__main__':
    # Example usage:
    original_lat = 37.7749
    original_lon = -122.4194
    distance_to_move_feet = 1000  # Replace with your desired distance
    bearing_to_move_degrees = 270  # Replace with your desired direction in degrees

    new_lat, new_lon = move_coordinates(original_lat, original_lon, distance_to_move_feet, bearing_to_move_degrees)

    print(f"Original Coordinates: {original_lat}, {original_lon}")
    print(f"New Coordinates: {new_lat}, {new_lon}")
    
    # I think this method doesn't work?
    distance, horizontal, vertical = haversine_distance_and_components(original_lat, original_lon, new_lat, new_lon)
    print("\n\n")
    print(f"Horizontal component: {horizontal:.5f} feet")
    print(f"Vertical component: {vertical:.5f} feet")
    print(f"Haversine distance between points: {distance:.5f}")