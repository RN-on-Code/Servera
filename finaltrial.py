import subprocess
import time
import googlemaps
from datetime import datetime
from twilio.rest import Client

# Function to read and process the most recent SMS message
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

            # Filter messages where "yeah" or "no" is present
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
 # Error executing ADB command

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
    # Check for "From:" in the message
    if 'From:' in message:
        # Find the start index after "From:"
        start_index = message.find('From:') + len('From:')
        
        # Find the end index starting from the calculated start index
        end_index = message.find('>', start_index)
        
        # Check if both start and end indices are found
        if start_index != -1 and end_index != -1:
            # Extract the contact information
            contact = message[start_index:end_index].strip()
            return contact
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
# Function to check for "yeah" or "no" responses from the same contact number
# Function to check for "yeah" or "no" responses from the same contact number
def check_for_responses(contact_number):
    print("Checking for responses...")
    # Wait for the response for a specific time frame (e.g., 5 minutes)
    time.sleep(20)  # 5 minutes

    # Check for responses in your inbox
    recent_byroad_sms, _, recent_response_sms = read_recent_sms()
    print("Response message:", recent_response_sms)  # Fix the variable name here

    # Extract contact from the response message
    sender_contact_response = parse_contact(recent_response_sms)
    print(sender_contact_response)

    if sender_contact_response and sender_contact_response == contact_number:
        response_message = recent_response_sms.lower()  # Convert to lowercase for case-insensitive comparison
        if "yeah" in response_message:
            return "yeah"
        elif "no" in response_message:
            return "no"
        else:
            return None
    else:
        return None




# Replace 'YOUR_API_KEY' with your actual Google Maps API key
api_key = 'AIzaSyC3TDYhGNQQcRkOxs7T1iTSLoOE5mIU-sE'

# Initialize with empty messages and addresses
current_byroad_message = None
byroad_address = None
processed_byroad_message = False
byroad_contact_number = None

# Main loop to continuously read and process the most recent SMS messages
# Main loop to continuously read and process the most recent SMS messages
# Main loop to continuously read and process the most recent SMS messages
while True:
    recent_byroad_sms, _, recent_response_sms = read_recent_sms()

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
                send_twilio_sms(byroad_contact_number, f"Hi there! The fare for your trip from {from_location.strip()} to {to_location.strip()} is Rs. {fare:.2f}. Should we proceed to find you a ride? (Reply with 'yeah' or 'no')")

                # Set the flag to True to indicate that the current Byroad message has been processed
                processed_byroad_message = True

                # Check for "yeah" or "no" responses in your inbox
                response = check_for_responses(byroad_contact_number)

                if response:
                    print(f"Got response '{response}' from {byroad_contact_number}")
                    if response == "yeah":
                        # Process "yeah" response logic
                        print("Processing 'yeah' response logic.")
                    elif response == "no":
                        # Process "no" response logic
                        print("Processing 'no' response logic.")

            else:
                print("Failed to calculate distance.")
        else:
            print("Failed to extract locations")

    # Add a delay before checking for new messages again
    time.sleep(5)
