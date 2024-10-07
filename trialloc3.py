import requests

def get_address_from_google_maps_link(api_key, google_maps_link):
    # Extract latitude and longitude from the Google Maps link
    coordinates = google_maps_link.split('@')[1].split(',')[0:2]
    latitude, longitude = map(float, coordinates)

    # Make a request to the Google Maps Geocoding API
    api_url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}'
    response = requests.get(api_url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response and extract the formatted address
        result = response.json()
        if result['status'] == 'OK' and 'results' in result and result['results']:
            address = result['results'][0]['formatted_address']
            return address

    # If the request was not successful or no address found, return None
    return None

# Replace 'YOUR_API_KEY' with your actual Google Cloud API key
api_key = 'AIzaSyC3TDYhGNQQcRkOxs7T1iTSLoOE5mIU-sE'

# Example usage:
google_maps_link = 'https://www.google.com/maps/@18.8181772,76.7698374,7z/data=!4m2!7m1!2e1?hl=en&entry=ttu'
address = get_address_from_google_maps_link(api_key, google_maps_link)

if address:
    print(f'The address is: {address}')
else:
    print("Unable to retrieve the address.")
