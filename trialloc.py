import requests
from selenium import webdriver
import time
from urllib.parse import urlparse, parse_qs
from math import radians, sin, cos, sqrt, atan2

def get_distance_between_locations(link1, link2):
    # Start a new instance of Firefox browser
    driver = webdriver.Firefox()

    try:
        # Open the first Google Maps link
        driver.get(link1)

        # Wait for the page to load (you might need to adjust the sleep time)
        time.sleep(5)

        # Get the coordinates from the first link
        coordinates1 = extract_coordinates_from_google_maps_link(driver.current_url)

        # Open the second Google Maps link
        driver.get(link2)

        # Wait for the page to load (you might need to adjust the sleep time)
        time.sleep(5)

        # Get the coordinates from the second link
        coordinates2 = extract_coordinates_from_google_maps_link(driver.current_url)

        # Calculate the distance between the two sets of coordinates
        distance = calculate_distance(coordinates1, coordinates2)
        print(f"Distance between the two locations: {distance:.2f} km")

    finally:
        # Close the browser window
        driver.quit()

def extract_coordinates_from_google_maps_link(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Check if the latitude and longitude query parameters exist
    latitude = float(query_params.get('!3d', ['0'])[0])
    longitude = float(query_params.get('!2d', ['0'])[0])

    return latitude, longitude

def calculate_distance(coords1, coords2):
    # Haversine formula to calculate distance between two sets of coordinates
    lat1, lon1 = map(radians, coords1)
    lat2, lon2 = map(radians, coords2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Radius of the Earth in kilometers
    R = 6371.0

    # Calculate the distance
    distance = R * c

    return distance

# Replace 'YOUR_GOOGLE_MAPS_LINK_1' and 'YOUR_GOOGLE_MAPS_LINK_2' with the actual live location links
link1 = 'https://maps.app.goo.gl/2boUypds7uy8owr38'
link2 = 'https://maps.app.goo.gl/4bux8mZE2mnr1WgL8'

get_distance_between_locations(link1, link2)
