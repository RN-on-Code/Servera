from selenium import webdriver
import time
import requests
from urllib.parse import urlparse, parse_qs

def get_coordinates_and_address(api_key, google_maps_link):
    # Start a new instance of Firefox browser
    driver = webdriver.Firefox()

    try:
        # Open the Google Maps live location link
        driver.get(google_maps_link)

        # Wait for the page to load (you might need to adjust the sleep time)
        time.sleep(5)

        # Get the current URL from the web address section
        current_url = driver.current_url
        print("Current URL:", current_url)

        # Convert the URL to the 'place' format
        place_url = convert_to_place_format(current_url)
        print("Place URL:", place_url)

        # Fetch the address from the 'place' format URL using the logic from the second code
        address = get_address_from_google_maps_link1(api_key, current_url)
        print("Address:", address)

    finally:
        # Close the browser window
        driver.quit()

def convert_to_place_format(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Check if the latitude and longitude query parameters exist
    latitude = float(query_params.get('!3d', ['0'])[0])
    longitude = float(query_params.get('!2d', ['0'])[0])

    # Format the URL in the 'place' format
    place_url = f"https://www.google.com/maps/place/{latitude},{longitude}"

    return place_url

def get_address_from_google_maps_link1(api_key, current_url):
    # Extract latitude and longitude from the place_url
    coordinates = current_url.split('@')[1].split(',')[0:2]
    latitude, longitude = map(float, coordinates)

    # Use the Google Maps Geocoding API to get the address
    geocoding_api_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}"
    response = requests.get(geocoding_api_url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response and extract the formatted address
        result = response.json()
        if result['status'] == 'OK' and 'results' in result and result['results']:
            address = result['results'][0]['formatted_address']
            return address

    # If the request was not successful or no address found, return None
    return None

# Replace 'YOUR_GOOGLE_MAPS_LINK' and 'YOUR_API_KEY' with the actual live location link and Google Maps API key
google_maps_link = 'https://maps.app.goo.gl/rEHN1JieSaKR8BKr5'
api_key = 'AIzaSyC3TDYhGNQQcRkOxs7T1iTSLoOE5mIU-sE'

get_coordinates_and_address(api_key, google_maps_link)
