import subprocess
import re
import time
import requests
from datetime import datetime
import queue
import threading
from twilio.rest import Client

# Twilio credentials
account_sid = 'AC23e2bdaf3b39ed2b4c310f9038e7c886'
auth_token = '6707926e946a2b965ec43dfd590ca633'
twilio_phone_number = '+12015813623'

client = Client(account_sid, auth_token)

def send_sms(to, body):
    message = client.messages.create(
        body=body,
        from_=twilio_phone_number,
        to=to
    )
    print(f"SMS sent to {to}: {message.sid}")

# ... (rest of your code)
def read_recent_sms(include_phone=False):
    adb_command = 'adb shell content query --uri content://sms/inbox --projection address,date_sent,body --sort date_sent'

    result = subprocess.run(adb_command, shell=True, capture_output=True, text=True, encoding='utf-8')

    if result.returncode == 0:
        if result.stdout:
            sms_messages = result.stdout.strip().split('\n')

            # Regex patterns for matching Byroad and Onroad messages
            byroad_pattern = re.compile(r"Byroad @(.+) @(.+) #(\d+)?")
            onroad_pattern = re.compile(r"Onroad &(.+) #(\d+)")
            response_pattern = re.compile(r"Yeah @(.+)", re.IGNORECASE)
            response_pattern2 = re.compile(r"(Yeah)", re.IGNORECASE)

            # Extract valid Byroad and Onroad messages
            valid_byroad_messages = [msg for msg in sms_messages if byroad_pattern.search(msg)]
            valid_onroad_messages = [msg for msg in sms_messages if onroad_pattern.search(msg)]
            valid_response_messages = [msg for msg in sms_messages if response_pattern.search(msg)]
            valid_response_messages2 = [msg for msg in sms_messages if response_pattern2.search(msg)]

            # Find the most recent Byroad, Onroad, and response messages
            most_recent_byroad_message = valid_byroad_messages[-1] if valid_byroad_messages else None
            most_recent_onroad_message = valid_onroad_messages[-1] if valid_onroad_messages else None
            most_recent_response_message = valid_response_messages[-1] if valid_response_messages else None
            most_recent_response_message2 = valid_response_messages2[-1] if valid_response_messages2 else None

            if include_phone:
                # If include_phone is True, return both versions of Byroad message
                return most_recent_byroad_message, most_recent_byroad_message, most_recent_response_message, most_recent_response_message2
            else:
                return most_recent_byroad_message, most_recent_onroad_message, most_recent_response_message, most_recent_response_message2
        else:
            return None, None, None, None  # No SMS messages found
    else:
        print(f"Error executing ADB command. Return code: {result.returncode}")
        print(f"Error details: {result.stderr}")
        return None, None, None, None

def extract_locations(byroad_message):
    if byroad_message:
        match = re.search(r"Byroad @(.+) @(.+) #(\d+)", byroad_message)
        if match:
            from_location = match.group(1).strip()
            to_location = match.group(2).strip()
            return from_location, to_location
    return None, None

def calculate_distance(origin, destination, api_key):
    base_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    params = {
        'origins': origin,
        'destinations': destination,
        'key': api_key,
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if response.status_code == 200 and data['status'] == 'OK':
        distance_text = data['rows'][0]['elements'][0]['distance']['text']
        return distance_text
    else:
        print(f"Error calculating distance: {data['error_message']}")
        return None

def calculate_fare(distance_text, price_per_km):
    try:
        distance_in_km = float(distance_text.split()[0])
        fare_price = distance_in_km * price_per_km
        return fare_price
    except ValueError:
        print("Error converting distance to a number.")
        return None
    
def calculate_eta(origin, destination, api_key):
    base_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    params = {
        'origins': origin,
        'destinations': destination,
        'key': api_key,
        'mode': 'driving',  # You can change the travel mode as needed
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if response.status_code == 200 and data['status'] == 'OK':
        duration_text = data['rows'][0]['elements'][0]['duration']['text']
        print(duration_text)
        return duration_text
    else:
        print(f"Error calculating duration: {data['error_message']}")
        return None



from datetime import datetime
import time

def extract_phone_number(byroad_message_with_phone, byroad_message_without_phone):
    if byroad_message_with_phone:
        match_with_phone = re.search(r"Byroad @.+ @.+ #(\d+)", byroad_message_with_phone)
        if match_with_phone:
            phone_number = match_with_phone.group(1).strip()
            return "+91" + phone_number
    elif byroad_message_without_phone:
        match_without_phone = re.search(r"Byroad @.+ @.+", byroad_message_without_phone)
        if match_without_phone:
            # Extract the phone number from the Byroad message
            return extract_phone_number_from_message(byroad_message_without_phone)
    return None


def extract_phone_number_from_message(byroad_message):
    # Extract the phone number from the Byroad message
    match = re.search(r"Byroad @.+ @.+ #(\d+)", byroad_message)
    if match:
        phone_number = match.group(1).strip()
        return "+91" + phone_number
    return None
def extract_response_phone_number(response_message):
    if response_message:
        match = re.search(r"address=(\+\d+)", response_message)
        if match:
            return match.group(1).strip()
    return None
def extract_onroad_phone_number(onroad_message):
    if onroad_message:
        match = re.search(r"Onroad &(.+) #(\d+)", onroad_message)
        if match:
            phone_number = match.group(2).strip()
            return "+91" + phone_number
    return None

def ask_to_proceed2():
    print("Hey, do you want to proceed?")
    question_timestamp1 = time.time()
    question_datetime1 = datetime.now()

    while time.time() - question_timestamp1 < 30:  # Check for 5 minutes
        _, _, _, onroad_message, response_message1, _ = read_recent_sms(include_phone=True)
        print(response_message1)
        onroad_phone_number = extract_onroad_phone_number(onroad_message)

        # Extract the phone number from the response message
        response_phone_number1 = extract_response_phone_number(response_message1)
        print(response_phone_number1)
        print(onroad_phone_number)

        if response_message1 is not None:
            response_parts1 = response_message1.split(',')

            if len(response_parts1) >= 2:
                try:
                    response_timestamp1 = int(response_parts1[1].split('=')[1].strip())
                    response_datetime1 = datetime.fromtimestamp(response_timestamp1 / 1000.0)
                    print(f"Response received at: {response_datetime1}")
                    if response_datetime1 > question_datetime1:
                        return response_message1, onroad_phone_number
                except (ValueError, IndexError):
                    print("Error extracting or converting response timestamp.")

        # Delay for 10 seconds before checking again
        time.sleep(10)

    return None, None


def ask_to_proceed():
    print("Hey, do you want to proceed?")
    question_timestamp = time.time()
    question_datetime = datetime.now()

    while time.time() - question_timestamp < 30:  # Check for 5 minutes
        byroad_message_with_phone, byroad_message_without_phone, _, response_message = read_recent_sms(include_phone=True)

        # Extract the phone number from both versions of the Byroad message
        byroad_phone_number_with_phone = extract_phone_number(byroad_message_with_phone, "")
        byroad_phone_number_without_phone = extract_phone_number("", byroad_message_without_phone)
        # Extract the phone number from the response message
        response_phone_number = extract_response_phone_number(response_message)

        print(response_phone_number)
        print(byroad_phone_number_with_phone)
        print(byroad_phone_number_without_phone)

        if response_message is not None:
            response_parts = response_message.split(',')

            if len(response_parts) >= 2:
                try:
                    response_timestamp = int(response_parts[1].split('=')[1].strip())
                    response_datetime = datetime.fromtimestamp(response_timestamp / 1000.0)
                    print(f"Response received at: {response_datetime}")

                    # Check if the response corresponds to the Byroad message with phone number
                    if response_phone_number == byroad_phone_number_with_phone:
                        ask_to_proceed2()
                        return response_message.lower()

                    # Check if the response corresponds to the Byroad message without phone number
                    elif response_phone_number == byroad_phone_number_without_phone:
                        ask_to_proceed2()
                        return response_message.lower()

                except (ValueError, IndexError):
                    print("Error extracting or converting response timestamp.")

        # Delay for 10 seconds before checking again
        time.sleep(10)

    return None



def process_byroad(api_key, price_per_km, message_queue):
    most_recent_byroad = None

    while True:
        new_byroad, _, _, new_byroad_has_phone = read_recent_sms()

        if new_byroad and new_byroad != most_recent_byroad:
            print(f"Most recent Byroad message found: {new_byroad}")

            # Extract "from" and "to" locations
            from_location, to_location = extract_locations(new_byroad)
            if from_location and to_location:
                print(f"From: {from_location}, To: {to_location}")

                # Extract phone number from Byroad message
                byroad_phone_number = extract_phone_number(new_byroad, new_byroad_has_phone)

                # Calculate distance
                distance_text = calculate_distance(from_location, to_location, api_key)
                if distance_text:
                    print(f"Distance: {distance_text}")

                    # Calculate fare price
                    fare_price = calculate_fare(distance_text, price_per_km)
                    if fare_price is not None:
                        print(f"Fare Price: Rs {fare_price:.2f}")

                        # Calculate ETA
                        eta = calculate_eta(from_location, to_location, api_key)
                        if eta:
                            print(f"ETA: {eta}")

                            # Ask if the user wants to proceed
                            response, onroad_phone_number = ask_to_proceed()
                            print(response, onroad_phone_number)
                            if response is not None and onroad_phone_number is not None:
                                print(f"User responded: {response}")

                                # Send SMS using Twilio
                                send_sms(byroad_phone_number, f"Your ride has been confirmed. ETA: {eta}")

            most_recent_byroad = new_byroad

        # Delay for 30 seconds before checking again
        time.sleep(30)


# ... (rest of your code)
def process_onroad(api_key, price_per_km, message_queue):
    most_recent_onroad = None

    while True:
        _, new_onroad, _, _ = read_recent_sms()

        if new_onroad and new_onroad != most_recent_onroad:
            print(f"Most recent roadon message found: {new_onroad}")

            # Extract "from" and "to" locations
           

def process_user_responses(message_queue):
    while True:
        _, _, _, new_response = read_recent_sms()

        if new_response:
            # Process the new response
            # ...
            message_queue.put(new_response)

        # Delay for 10 seconds before checking again
        time.sleep(10)

if __name__ == "__main__":
    google_maps_api_key = 'AIzaSyC3TDYhGNQQcRkOxs7T1iTSLoOE5mIU-sE'
    price_per_km = 20

    message_queue = queue.Queue()

    # Create threads for processing byroad, onroad, and user responses
    byroad_thread = threading.Thread(target=process_byroad, args=(google_maps_api_key, price_per_km, message_queue))
    onroad_thread = threading.Thread(target=process_onroad, args=(google_maps_api_key, price_per_km, message_queue))
    response_thread = threading.Thread(target=process_user_responses, args=(message_queue,))

    # Start the threads
    byroad_thread.start()
    onroad_thread.start()
    response_thread.start()
    

    # Wait for the threads to finish (this won't happen in this example as they run indefinitely)
    byroad_thread.join()
    onroad_thread.join()
    response_thread.join()

