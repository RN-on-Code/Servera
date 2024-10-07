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

# Function to parse contact from a message
def parse_contact(message):
    start_index = message.find('From:') + len('From:')
    end_index = message.find('>', start_index)
    if start_index != -1 and end_index != -1:
        contact = message[start_index:end_index].strip()
        return contact
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

# Function to find the nearest Onroad location for a given Byroad location
def find_nearest_onroad(api_key, byroad_address, onroad_messages):
    gmaps = googlemaps.Client(key=api_key)

    # Calculate distances between the Byroad location and all Onroad locations
    distances = [calculate_distance(api_key, byroad_address, extract_address(onroad_message)) for onroad_message in onroad_messages]

    # Find the index of the nearest Onroad location
    nearest_index = distances.index(min(distances))

    return onroad_messages[nearest_index]

# Function to send SMS using Twilio
def send_twilio_sms(to, body):
    account_sid = 'AC9732b9a5f922bf227132bde7205e6c01'
    auth_token = '4e43c05500ffc7faa6d50bf93a5c0d4f'

    # Create a Twilio client
    client = Client(account_sid, auth_token)

    # Replace 'YOUR_TWILIO_PHONE_NUMBER' with your Twilio phone number
    from_number = '+13346001562'

    # Send SMS with "Byroad" and the body after "Byroad"
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

# Function to check for a response in the inbox
def check_for_response(sender_contact):
    adb_command = f'adb shell content query --uri content://sms/inbox --projection address,body --where "address=\'{sender_contact}\'" --sort date_sent'

    result = subprocess.run(adb_command, shell=True, capture_output=True, text=True, encoding='utf-8')

    if result.returncode == 0:
        if result.stdout:
            response_messages = result.stdout.strip().split('\n')

            # Filter messages that contain "yes" or "no"
            valid_responses = [msg for msg in response_messages if "yes" in msg.lower() or "no" in msg.lower()]

            if valid_responses:
                most_recent_response = valid_responses[-1]
                return most_recent_response
            else:
                return None
        else:
            return None  # No SMS messages found
    else:
        print(f"Error executing ADB command to check for response. Return code: {result.returncode}")
        print(f"Error details: {result.stderr}")
        return None

# Function to check for a response in the inbox within a specific timeframe
def check_for_response_within_timeframe(sender_contact, start_time, timeframe_minutes=2):
    end_time = start_time + timedelta(minutes=timeframe_minutes)

    while datetime.now() < end_time:
        response_message = check_for_response(sender_contact)

        if response_message is not None:
            print(f"Got response: {response_message}")
            # Process the response (e.g., determine if it's 'yes' or 'no')
            # Update the relevant logic based on the response
            return response_message

        # Add a delay before checking for a response again
        time.sleep(2)

    return None  # No response within the specified timeframe

# Replace 'YOUR_API_KEY' with your actual Google Maps API key
api_key = 'AIzaSyC3TDYhGNQQcRkOxs7T1iTSLoOE5mIU-sE'

# Initialize with empty messages and addresses
current_byroad_message = None
current_onroad_message = None
byroad_address = None
onroad_address = None
processed_byroad_message = False 
onroad_contact_number = None
sender_contact = None
byroad_message_timestamp = None

# Main loop to continuously read and process the most recent SMS messages
while True:
    recent_byroad_sms, recent_onroad_sms, valid_onroad_messages = read_recent_sms()

    if recent_byroad_sms is not None and recent_byroad_sms != current_byroad_message:
        current_byroad_message = recent_byroad_sms
        processed_byroad_message = False
        byroad_message_timestamp = datetime.now()
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

                send_twilio_sms(byroad_contact_number, f"Hi there! The fare for your trip from {from_location.strip()} to {to_location.strip()} is Rs. {fare:.2f}. Should we proceed to find you a ride? (Reply with 'yes' or 'no')")

                processed_byroad_message = True

                # Check for a response within a 2-minute timeframe
                response_message = check_for_response_within_timeframe(byroad_contact_number, datetime.now())

                if response_message is not None:
                    print(f"Got response within 2 minutes: {response_message}")

            else:
                print("Failed to calculate distance.")
        else:
            print("Failed to extract locations.")
    
    # Add a delay before checking for new messages again
    time.sleep(5)
