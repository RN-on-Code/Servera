import googlemaps
from datetime import datetime

def calculate_distance(api_key, origin, destination, mode="driving", departure_time=None):
    gmaps = googlemaps.Client(key=api_key)

    # Make a request to the Distance Matrix API
    result = gmaps.distance_matrix(
        origins=origin,
        destinations=destination,
        mode=mode,
        departure_time=departure_time,
    )

    # Extract the distance value from the response
    distance = result['rows'][0]['elements'][0]['distance']['value']

    # Convert distance from meters to kilometers
    distance_km = distance / 1000.0

    return distance_km

# Replace 'YOUR_API_KEY' with your actual API key
api_key = 'AIzaSyC3TDYhGNQQcRkOxs7T1iTSLoOE5mIU-sE'

# Specify the origin and destination
origin = "San Francisco, CA"
destination = "Los Angeles, CA"

# You can specify the travel mode (default is "driving") and departure time
mode = "driving"
departure_time = datetime.now()

# Calculate the distance
distance = calculate_distance(api_key, origin, destination, mode, departure_time)

print(f"The driving distance between {origin} and {destination} is {distance:.2f} km.")

