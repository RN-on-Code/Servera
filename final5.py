import subprocess
import time
import googlemaps
from datetime import datetime
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

            valid_byroad_messages = [msg for msg in sms_messages if "Byroad" in msg and '@' in msg and '#' in msg and 'Sent from your Twilio trial account' not in msg]
            valid_onroad_messages = [msg for msg in sms_messages if "Onroad" in msg and '@' in msg and '#' in msg and 'Sent from your Twilio trial account' not in msg]
            valid_response_messages = [msg for msg in sms_messages if ("yeah" in msg.lower() or "no" in msg.lower()) and 'Sent from your Twilio trial account' not in msg]

            if valid_byroad_messages:
                most_recent_byroad_message = valid_byroad_messages[-1]
            else:
                most_recent_byroad_message = None

            if valid_onroad_messages:
                most_recent_onroad_message = valid_onroad_messages[-1]
            else:
                most_recent_onroad_message = None

            if valid_response_messages:
                most_recent_response_message = valid_response_messages[-1]
            else:
                most_recent_response_message = None

            return most_recent_byroad_message, most_recent_onroad_message, most_recent_response_message
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

# Function to parse contact from a message
def parse_contact(response_message):
    # Check if the response message contains "From:"
    if 'From:' in response_message:
        # Find the start index after "From:"
        start_index = response_message.find('From:') + len('From:')
        
        # Find the end index starting from the calculated start index
        end_index = response_message.find('>', start_index)
        
        # Check if both start and end indices are found
        if start_index != -1 and end_index != -1:
            # Extract the contact information
            contact = response_message[start_index:end_index].strip()
            return contact
    return None



# Function to calculate distance between two locations
def calculate_distance(api_key, origin, destination, mode="driving", departure_time=None):
    try:
        gmaps = googlemaps.Client(key=api_key)
        result = gmaps.distance_matrix(
            origins=origin,
            destinations=destination,
            mode=mode,
            departure_time=departure_time,
        )

        if result['status'] == 'OK':
            distance = result['rows'][0]['elements'][0]['distance']['value']
            distance_km = distance / 1000.0
            return distance_km
        else:
            print(f"Distance calculation failed. API status: {result['status']}")
            return None
    except Exception as e:
        print(f"Error during distance calculation: {e}")
        return None

# Function to find the nearest Onroad location for a given Byroad location
def find_nearest_onroad(api_key, byroad_address, onroad_messages):
    gmaps = googlemaps.Client(key=api_key)
    distances = [calculate_distance(api_key, byroad_address, extract_address(onroad_message)) for onroad_message in onroad_messages]
    nearest_index = distances.index(min(distances))
    return onroad_messages[nearest_index]

# Function to send SMS using Twilio
def send_twilio_sms(to, body):
    account_sid = 'AC9732b9a5f922bf227132bde7205e6c01'
    auth_token = '4e43c05500ffc7faa6d50bf93a5c0d4f'
    client = Client(account_sid, auth_token)
    from_number = '+13346001562'
    body_with_byroad = f"Byroad {body.split('Byroad', 1)[-1].strip()}"
    message = client.messages.create(
        body=body_with_byroad,
        from_=from_number,
        to=to
    )
    print(f"Twilio SMS sent to {to}. SID: {message.sid}")

# Function to calculate fare price based on distance
def calculate_fare(distance, rate_per_km=5):
    fare = distance * rate_per_km
    return fare

# Function to check for "yeah" or "no" responses from the same contact number
def check_for_responses(contact):
    print("Checking for responses...")
    time.sleep(2)

    recent_byroad_sms, _, recent_response_sms = read_recent_sms()
    print("Response message:", recent_response_sms)

    # Extract contact number from the response message
    sender_contact_response = recent_response_sms.split('address=')[1].split(',', 1)[0].strip()
    print("Sender Contact Response:", sender_contact_response)

    if sender_contact_response and sender_contact_response == contact:
        response_message = recent_response_sms.lower()  # Convert to lowercase for case-insensitive comparison
        if "yeah" in response_message:
            return "yeah"
        elif "no" in response_message:
            return "no"
        else:
            return None
    else:
        return None




# Function to get coordinates and address from Google Maps live location link
# Function to get coordinates and address from Google Maps live location link
def get_coordinates_and_address(api_key, google_maps_link):
    driver = webdriver.Firefox()

    try:
        driver.get(google_maps_link)
        time.sleep(5)
        current_url = driver.current_url
        print("Current URL:", current_url)
        place_url = convert_to_place_format(current_url)
        print("Place URL:", place_url)
        address = get_address_from_google_maps_link(api_key, current_url)
        try:
            # Try to print the original address
            print("Address:", address)
        except UnicodeEncodeError:
            # If UnicodeEncodeError occurs, print a modified version
            print("Address (ASCII only):", address.encode('ascii', 'replace').decode('utf-8'))

        return place_url, address

    finally:
        driver.quit()


# Function to convert the URL to the 'place' format
def convert_to_place_format(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    latitude = float(query_params.get('!3d', ['0'])[0])
    longitude = float(query_params.get('!2d', ['0'])[0])
    place_url = f"https://www.google.com/maps/place/{latitude},{longitude}"
    return place_url

# Function to extract address from Google Maps live location link
def get_address_from_google_maps_link(api_key, current_url):
    coordinates = current_url.split('@')[1].split(',')[0:2]
    latitude, longitude = map(float, coordinates)
    geocoding_api_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}"
    response = requests.get(geocoding_api_url)
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'OK' and 'results' in result and result['results']:
            address = result['results'][0]['formatted_address']
            return address

    return None

# Function to process "yeah" responses
#
    nearest_onroad_message = find_nearest_onroad(api_key, from_location, onroad_messages)

    if nearest_onroad_message:
        live_location_link = extract_live_location_link(nearest_onroad_message)
        coordinates, onroad_address = get_coordinates_and_address(api_key, live_location_link)
        onroad_contact_number = extract_contact_number(nearest_onroad_message)

        if onroad_contact_number:
            send_twilio_sms(onroad_contact_number, f"Hi there! A user needs a ride from {from_location.strip()} to {to_location.strip()}.")
            print(f"SMS sent to {onroad_contact_number} with from and to locations.")

# Function to extract live location link from an onroad message
def extract_live_location_link(onroad_message):
    print(onroad_message) # Print the onroad_message for debugging
    

    start_index = onroad_message.find('@') + 1
    end_index = onroad_message.find('#')

    

    if start_index != -1 and end_index != -1:
        live_location_link = onroad_message[start_index:end_index].strip()
        print("Live Location Link:", repr(live_location_link))  # Use repr to show whitespace
        return live_location_link
    else:
        return None


# (Your existing code...)

# Function to process "yeah" responses
def process_yeah_response(api_key, onroad_messages, from_location, to_location):
    # List to store addresses extracted from onroad messages
    onroad_addresses = []
    # List to store distances for each onroad location
    distances = []

    
    live_location_link = extract_live_location_link(onroad_messages)

    if live_location_link:
            _, onroad_address = get_coordinates_and_address(api_key, live_location_link)

            if onroad_address:
                onroad_addresses.append(onroad_address)
                # Calculate distance between the byroad "from" location and onroad location
                distance = calculate_distance(api_key, from_location, onroad_address)
                distances.append(distance)

    if onroad_addresses and distances:
        # Print all the onroad locations and their distances
        for i in range(len(onroad_addresses)):
            print(f"Onroad Location: {onroad_addresses[i]}")
            print(f"Distance from Byroad 'from' location: {distances[i]:.2f} km")
            print("----------")

        # Find the index of the smallest distance
        nearest_index = distances.index(min(distances))

        # Print the smallest distance and corresponding onroad details
        print(f"The smallest distance is {distances[nearest_index]:.2f} km.")
        print(f"Nearest Onroad Message: {onroad_messages[nearest_index]}")
        print(f"Nearest Onroad Address: {onroad_addresses[nearest_index]}")

    else:
        print("No valid onroad addresses found.")
# (Your existing code...)

# Replace 'YOUR_API_KEY' with your actual Google Maps API key
api_key = 'AIzaSyC3TDYhGNQQcRkOxs7T1iTSLoOE5mIU-sE'

# Initialize with empty messages and addresses
current_byroad_message = None
byroad_address = None
processed_byroad_message = False
byroad_contact_number = None

# Main loop to continuously read and process the most recent SMS messages
while True:
    recent_byroad_sms, _, recent_response_sms = read_recent_sms()

    if recent_byroad_sms is not None and recent_byroad_sms != current_byroad_message:
        current_byroad_message = recent_byroad_sms
        processed_byroad_message = False

        print("Most recent valid Byroad SMS message:")
        print(current_byroad_message)

        byroad_address = extract_address(current_byroad_message)
        if byroad_address:
            print(f"Extracted Byroad Address: {byroad_address}") 
        byroad_contact_number = extract_contact_number(current_byroad_message)
        if byroad_contact_number:
            print(f"Extracted Byroad Contact Number: {byroad_contact_number}")

        locations = byroad_address.split('@')
        if len(locations) == 2:
            from_location, to_location = locations
            print(f"From Location: {from_location.strip()}")
            print(f"To Location: {to_location.strip()}")

            distance = calculate_distance(api_key, from_location, to_location, mode="driving", departure_time=datetime.now())

            if distance is not None:
                print(f"The distance between {from_location.strip()} and {to_location.strip()} is {distance:.2f} km.")

                fare = calculate_fare(distance)
                print(f"The fare for this trip is Rs. {fare:.2f}.")

                send_twilio_sms(byroad_contact_number, f"Hi there! The fare for your trip from {from_location.strip()} to {to_location.strip()} is Rs. {fare:.2f}. Should we proceed to find you a ride? (Reply with 'yeah' or 'no')")

                processed_byroad_message = True

                response = check_for_responses(byroad_contact_number)

                if response:
                    print(f"Got response '{response}' from {byroad_contact_number}")
                    if response == "yeah":
                        _, onroad_messages, _ = read_recent_sms()

                        process_yeah_response(api_key, onroad_messages, from_location, to_location)
                    elif response == "no":
                        print("Processing 'no' response logic.")

            else:
                print("Failed to calculate distance.")
        else:
            print("Failed to extract locations")

    time.sleep(5)
