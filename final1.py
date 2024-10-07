import subprocess
import time
import googlemaps
from datetime import datetime, timedelta
from twilio.rest import Client
from selenium import webdriver
import requests
from urllib.parse import urlparse, parse_qs

# Function to read and process the most recent SMS message
def read_recent_sms():
    adb_command = 'adb shell content query --uri content://sms/inbox --projection address,date_sent,body --sort date_sent'

    result = subprocess.run(adb_command, shell=True, capture_output=True, text=True, encoding='utf-8')

    if result.returncode == 0:
        if result.stdout:
            sms_messages = result.stdout.strip().split('\n')

            # Filter messages where "Byroad" or "Onroad" is present and has "@" and "#" symbols
            valid_byroad_messages = [msg for msg in sms_messages if "Byroad" in msg and '@' in msg and '#' in msg and 'Sent from your Twilio trial account' not in msg]
            valid_onroad_messages = [msg for msg in sms_messages if "Onroad" in msg and '@' in msg and '#' in msg and 'Sent from your Twilio trial account' not in msg]

            if valid_byroad_messages:
                most_recent_byroad_message = valid_byroad_messages[-1]
            else:
                most_recent_byroad_message = None

            if valid_onroad_messages:
                most_recent_onroad_message = valid_onroad_messages[-1]
            else:
                most_recent_onroad_message = None

            return most_recent_byroad_message, most_recent_onroad_message, valid_onroad_messages
        else:
            return None, None, None  # No SMS messages found
    else:
        print(f"Error executing ADB command. Return code: {result.returncode}")
        print(f"Error details: {result.stderr}")
        return None, None, None  # Error executing ADB command

# Function to extract address after "@" in a message
def extract_address(message):
    start_index = message.find('@') + 1
    end_index = message.find('#')
    if start_index != -1 and end_index != -1:
        address = message[start_index:end_index].strip()
        return address
    else:
        return None

# Function to extract contact number after "#" in a message
def extract_contact_number(message):
        start_index = message.find('#') + 1
        if start_index != -1:
            contact_number = message[start_index:].strip()
            # Add "+91" to the extracted contact number
            return "+91" + contact_number
        else:
            return None

# Function to calculate distance between two locations
def calculate_distance(api_key, origin, destination, mode="driving", departure_time=None):
    try:
        gmaps = googlemaps.Client(key=api_key)

        # Make a request to the Distance Matrix API
        result = gmaps.distance_matrix(
            origins=origin,
            destinations=destination,
            mode=mode,
            departure_time=departure_time,
        )

        # Check if the API request was successful
        if result['status'] == 'OK':
            # Extract the distance value from the response
            distance = result['rows'][0]['elements'][0]['distance']['value']

            # Convert distance from meters to kilometers
            distance_km = distance / 1000.0

            return distance_km
        else:
            print(f"Distance calculation failed. API status: {result['status']}")
            return None
    except Exception as e:
        print(f"Error during distance calculation: {e}")
        return None

# Function to calculate travel time between two locations
def calculate_travel_time(api_key, origin, destination, mode="driving", departure_time=None):
    try:
        gmaps = googlemaps.Client(key=api_key)

        # Make a request to the Distance Matrix API
        result = gmaps.distance_matrix(
            origins=origin,
            destinations=destination,
            mode=mode,
            departure_time=departure_time,
        )

        # Check if the API request was successful
        if result['status'] == 'OK':
            # Extract the duration value from the response
            duration_seconds = result['rows'][0]['elements'][0]['duration']['value']

            # Convert duration from seconds to minutes
            duration_minutes = duration_seconds / 60.0

            return duration_minutes
        else:
            print(f"Travel time calculation failed. API status: {result['status']}")
            return None
    except Exception as e:
        print(f"Error during travel time calculation: {e}")
        return None

# Function to calculate fare based on distance
def calculate_fare(distance):
    # Assuming fare rate is Rs. 5 per kilometer
    fare_rate = 5.0
    fare = distance * fare_rate
    return fare

# Function to convert Google Maps live location link to 'place' format
def convert_to_place_format(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Check if the latitude and longitude query parameters exist
    latitude = float(query_params.get('!3d', ['0'])[0])
    longitude = float(query_params.get('!2d', ['0'])[0])

    # Format the URL in the 'place' format
    place_url = f"https://www.google.com/maps/place/{latitude},{longitude}"

    return place_url

# Function to get address from Google Maps live location link
def get_address_from_google_maps_link(api_key, current_url):
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

# Function to get coordinates and address from Google Maps live location link
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
        address = get_address_from_google_maps_link(api_key, current_url)
        print("Address:", address)

        # Return coordinates and address
        coordinates_and_address = {'coordinates': place_url, 'address': address}
        return coordinates_and_address

    finally:
        # Close the browser window
        driver.quit()

# Function to send SMS using Twilio
def send_twilio_sms(to, body):
    account_sid = 'AC9732b9a5f922bf227132bde7205e6c01'
    auth_token = '4e43c05500ffc7faa6d50bf93a5c0d4f'

    # Create a Twilio client
    client = Client(account_sid, auth_token)

    # Replace 'YOUR_TWILIO_PHONE_NUMBER' with your Twilio phone number
    from_number = '+13346001562'

    # Send SMS with the body after "Byroad"
    body_with_byroad = f"Byroad {body.split('Byroad', 1)[-1].strip()}"

    message = client.messages.create(
        body=body_with_byroad,
        from_=from_number,
        to=to
    )

    print(f"Twilio SMS sent to {to}. SID: {message.sid}")

# Function to find the nearest onroad customer and send a notification
def find_nearest_customer(api_key, onroad_address, onroad_messages):
    gmaps = googlemaps.Client(key=api_key)

    # List to store live location links and contact numbers
    live_location_links = []
    contact_numbers = []

    # Iterate through onroad messages to extract live location links and contact numbers
    for onroad_message in onroad_messages:
        # Extract live location link after "@" in Onroad message
        live_location_link = onroad_message.split('@')[1].split()[0]
        live_location_links.append(live_location_link)

        # Extract contact number after "#" in Onroad message
        contact_number = extract_contact_number(onroad_message)
        contact_numbers.append(contact_number)

    # Iterate through stored live location links
    for i, live_location_link in enumerate(live_location_links):
        # Get coordinates and address from live location link
        onroad_coordinates = get_coordinates_and_address(api_key, live_location_link)
        onroad_address_from_link = onroad_coordinates['address']

        # Calculate distance between Onroad location and customer's location
        distance = calculate_distance(api_key, onroad_address, onroad_address_from_link, mode="driving", departure_time=datetime.now())

        if distance is not None:
            print(f"Distance between Onroad location and customer {i + 1} is {distance:.2f} km.")

            # Notify the onroad customer with relevant information
            send_twilio_sms(contact_numbers[i], f"You have got a customer!\nFare: Rs. {calculate_fare(distance):.2f}\nFrom: {onroad_address}\nTo: {onroad_address_from_link}")
        else:
            print(f"Failed to calculate distance between Onroad location and customer {i + 1}.")

# Replace 'YOUR_API_KEY' with your actual Google Maps API key
api_key = 'AIzaSyC3TDYhGNQQcRkOxs7T1iTSLoOE5mIU-sE'

# Initialize with empty messages and addresses
current_byroad_message = None
current_onroad_message = None
byroad_address = None
onroad_address = None
processed_byroad_message = False  # Flag to track whether the current Byroad message has been processed

# Main loop to continuously read and process the most recent SMS messages
while True:
    recent_byroad_sms, recent_onroad_sms, valid_onroad_messages = read_recent_sms()

    if recent_byroad_sms is not None and recent_byroad_sms != current_byroad_message:
        current_byroad_message = recent_byroad_sms
        processed_byroad_message = False  # Reset the flag since it's a new Byroad message
        print("Most recent valid Byroad SMS message:")
        print(current_byroad_message)

        # Extract address after "@" in Byroad message
        byroad_address = extract_address(current_byroad_message)
        if byroad_address:
            print(f"Extracted Byroad Address: {byroad_address}")

        # Extract contact number after "#" in Byroad message
        byroad_contact_number = extract_contact_number(current_byroad_message)
        if byroad_contact_number:
            print(f"Extracted Byroad Contact Number: {byroad_contact_number}")

        # Extract locations from Byroad message
        locations = byroad_address.split('@')
        if len(locations) == 2:
            from_location, to_location = locations
            print(f"From Location: {from_location.strip()}")
            print(f"To Location: {to_location.strip()}")

            # Calculate distance between "From" and "To" locations
            distance = calculate_distance(api_key, from_location, to_location, mode="driving", departure_time=datetime.now())

            if distance is not None:
                print(f"The distance between {from_location.strip()} and {to_location.strip()} is {distance:.2f} km.")

                # Calculate fare based on distance
                fare = calculate_fare(distance)
                print(f"The fare for this trip is Rs. {fare:.2f}.")

                # Send SMS using Twilio to the contact number extracted from the nearest Onroad message
                send_twilio_sms(byroad_contact_number, f"Hi there! The fare for your trip from {from_location.strip()} to {to_location.strip()} is Rs. {fare:.2f}.")

                # Set the flag to True to indicate that the current Byroad message has been processed
                processed_byroad_message = True
        # ... (Same as before)

    if recent_onroad_sms is not None and recent_onroad_sms != current_onroad_message:
        current_onroad_message = recent_onroad_sms
        print("Most recent valid Onroad SMS message:")
        print(current_onroad_message)

        # Extract address after "@" in Onroad message
        onroad_address = extract_address(current_onroad_message)
        if onroad_address:
            print(f"Extracted Onroad Address: {onroad_address}")

        # Extract contact number after "#" in Onroad message
        onroad_contact_number = extract_contact_number(current_onroad_message)
        if onroad_contact_number:
            print(f"Extracted Onroad Contact Number: {onroad_contact_number}")

    # If both addresses are extracted and the current Byroad message hasn't been processed yet, process it
    if byroad_address and onroad_address and valid_onroad_messages and not processed_byroad_message:
        # ... (Same as before)

        # Ask the user whether to proceed and find a ride
        send_twilio_sms(byroad_contact_number, f"Hi there! The fare for your trip from {from_location.strip()} to {to_location.strip()} is Rs. {fare:.2f}. Should we proceed and find you a ride? Reply with 'Yes' or 'No'.")

        # Set the flag to True to indicate that the current Byroad message has been processed
        processed_byroad_message = True

    # If the user responds with 'Yes', find the nearest onroad customer and notify them
    if processed_byroad_message and recent_byroad_sms and recent_byroad_sms.lower().strip() == 'yes':
        find_nearest_customer(api_key, onroad_address, valid_onroad_messages)

    # Add a delay before checking for new messages again
    time.sleep(5)