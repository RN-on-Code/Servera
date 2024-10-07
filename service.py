import subprocess
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.distance import geodesic
import re
from twilio.rest import Client

# Twilio credentials
account_sid = 'AC9732b9a5f922bf227132bde7205e6c01'
auth_token = '4e43c05500ffc7faa6d50bf93a5c0d4f'
twilio_phone_number = '+13346001562'
client = Client(account_sid, auth_token)

def get_coordinates(address):
    geolocator = Nominatim(user_agent="your_app_name")
    try:
        location = geolocator.geocode(address)
        return (location.latitude, location.longitude)
    except (AttributeError, GeocoderTimedOut):
        return None

def calculate_distance(coords1, coords2):
    if coords1 is not None and coords2 is not None:
        distance = geodesic(coords1, coords2).kilometers
        return distance
    else:
        return None

def process_sms(sms_content):
    match = re.search(r"@(.+) #(\d+)", sms_content)
    if match:
        address = match.group(1).strip()
        phone_number = match.group(2).strip()
        return address, phone_number
    else:
        return None, None

# Function to send SMS using Twilio
def send_twilio_sms(to_phone_number, message):
    # Add the country code, assuming +91 for India
    to_phone_number_with_country_code = '+91' + to_phone_number
    
    message = client.messages.create(
        body=message,
        from_=twilio_phone_number,
        to=to_phone_number_with_country_code
    )
    print(f"Twilio Message SID: {message.sid}")

# Function to read and process the most recent Onroad and Byroad SMS messages
def read_recent_road_sms(onroad_locations, last_byroad_message, last_onroad_message):
    adb_command = 'adb shell content query --uri content://sms/inbox --projection date_sent,body'

    result = subprocess.run(adb_command, shell=True, capture_output=True, text=True, encoding='utf-8')

    if result.returncode == 0:
        if result.stdout:
            sms_messages = result.stdout.strip().split('\n')

            date_sent_values = [msg.split('|')[1].strip() if len(msg.split('|')) > 1 else '' for msg in sms_messages]
            sorted_messages = sorted(zip(date_sent_values, sms_messages), key=lambda x: x[0], reverse=True)

            byroad_messages = [msg[1] for msg in sorted_messages if "Byroad" in msg[1]]
            onroad_messages = [msg[1] for msg in sorted_messages if "Onroad" in msg[1]]

            most_recent_byroad_message = byroad_messages[0] if byroad_messages else None
            most_recent_onroad_message = onroad_messages[0] if onroad_messages else None

            if most_recent_onroad_message != last_onroad_message:
                onroad_location, onroad_phone_number = process_sms(most_recent_onroad_message)
                if onroad_location:
                    onroad_coords = get_coordinates(onroad_location)
                    if onroad_coords:
                        onroad_locations.append(onroad_coords)
                        last_onroad_message = most_recent_onroad_message
                        print(f"Recent Onroad SMS: {last_onroad_message}")
                        print(f"Onroad Location: {onroad_location} ({onroad_coords[0]}, {onroad_coords[1]})")

            if most_recent_byroad_message != last_byroad_message:
                address1, byroad_phone_number = process_sms(most_recent_byroad_message)
                if address1:
                    coords1 = get_coordinates(address1)
                    if coords1:
                        lat1, lon1 = coords1
                        print(f"Recent Byroad SMS: {most_recent_byroad_message}")
                        print(f"Byroad Location: {address1} ({lat1}, {lon1})")

                        closest_onroad_location = None
                        min_distance = float('inf')

                        for onroad_coords in onroad_locations:
                            distance = calculate_distance(coords1, onroad_coords)
                            if distance is not None and distance < min_distance:
                                min_distance = distance
                                closest_onroad_location = onroad_coords
                                closest_onroad_message = last_onroad_message

                        if closest_onroad_location is not None and (most_recent_byroad_message != last_byroad_message or closest_onroad_message == most_recent_onroad_message):
                            print(f"Closest Onroad Location: {closest_onroad_location} ({min_distance:.2f} kilometers)")
                            print(last_onroad_message)
                            print(most_recent_onroad_message)
                            print(closest_onroad_location)
                            

                            # Send the byroad message to the phone number from the closest onroad location
                            if onroad_phone_number:
                                print('hi')

                                #byroad_message = f"Byroad @{address1} #{byroad_phone_number}."
                                #send_twilio_sms(onroad_phone_number, byroad_message)

                            last_byroad_message = most_recent_byroad_message
                        
                       

            return last_byroad_message, last_onroad_message
        else:
            print("No SMS messages found")
            return None, None  # No SMS messages found
    else:
        print(f"Error executing ADB command. Return code: {result.returncode}")
        print(f"Error details: {result.stderr}")
        return None, None  # Error executing ADB command

# Initialize variables
onroad_locations = []
last_byroad_message = None
last_onroad_message = None

# Main loop to continuously display the most recent Onroad and Byroad SMS messages
while True:
    last_byroad_message, last_onroad_message = read_recent_road_sms(onroad_locations, last_byroad_message, last_onroad_message)
    

    # Add a delay (e.g., 5 seconds) before checking for new messages again
    time.sleep(5)
    
