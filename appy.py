import subprocess 
import re 
import time 
import requests 
from datetime import datetime
import queue
from twilio.rest import Client
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process 
from concurrent.futures import ProcessPoolExecutor
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
def statements(total_fare_price, from_location, to_location, ttc):
    statement1 = f"Thank you for considering us. Your total fare becomes {total_fare_price} /-\n . Should we proceed find you a ride?\n Reply (Yes) to proceed to +919970638387 else ignore. "

    statement2 = f"Hey! we got a passenger.\n From: {from_location}\n To: {to_location}\n Travel time: {ttc}\n Total fare: {total_fare_price}"
    statement3 = f"Sorry! we didn't receive any response for your ride confirmation. May be you can try it later."
    return statement1, statement2, statement3
def statements1(corresponding_response_message_noplate, corresponding_response_message_phoneno, response_interval):
    statement4 = f"Your ride is confirmed.\n Vehicle No. Plate: {corresponding_response_message_noplate}\n Driver's Contact: {corresponding_response_message_phoneno}\n. Will be within {response_interval} to you."
    statement5 = f"Your ride has been cancelled.\n Thank you for considering us."
    statement6 = f"Sorry! The ride has been cancelled.\n Stay tuned we'll let you know about any new customer."
    statement7 = f"Happy Journey...!"
    statement8 = f"Sorry! no rides available at this moment"
    return statement4, statement5, statement6, statement7, statement8


app = Flask(__name__)

@app.route('/sms', methods=['POST'])
def receive_sms():
    # Get the JSON data sent from the Android app
     
    data = request.get_json()

    # Process the received data
    most_recent_byroad_message, valid_onroad_messages, most_recent_response_message, most_recent_response_message2, most_recent_cancel_message = read_recent_sms(data)

    # Respond back to the client
    return jsonify({
        "most_recent_byroad_message": most_recent_byroad_message,
        "valid_onroad_messages": valid_onroad_messages,
        "most_recent_response_message": most_recent_response_message,
        "most_recent_response_message2": most_recent_response_message2,
        "most_recent_cancel_message": most_recent_cancel_message
    })

def read_recent_sms(data):
    # Assuming 'data' is the JSON payload received from your Android app
    if data and 'message' in data:
        message = data['message']
        
        # Regex patterns for matching Byroad and Onroad messages
        byroad_pattern1 = re.compile(r"Byroad @(.+) @(.+)(?: #(\d+))?")
        byroad_pattern2 = re.compile(r"Byroad @(.+) @(.+)")
        onroad_pattern = re.compile(r"Onroad &(.+) #(\d+)")
        response_pattern = re.compile(r"Ok @(.+)", re.IGNORECASE)
        response_pattern2 = re.compile(r"(Yeah)", re.IGNORECASE)
        cancel_message_pattern = re.compile(r"Byroad @Cancel")

        # Initialize lists for valid messages
        valid_byroad_messages = []
        valid_onroad_messages = []
        valid_response_messages = []
        valid_response_messages2 = []
        valid_cancel_messages = []

        # Check the message against the patterns
        if byroad_pattern1.search(message) or byroad_pattern2.search(message):
            valid_byroad_messages.append(message)
        if onroad_pattern.search(message):
            valid_onroad_messages.append(message)
        if response_pattern.search(message):
            valid_response_messages.append(message)
        if response_pattern2.search(message):
            valid_response_messages2.append(message)
        if cancel_message_pattern.search(message):
            valid_cancel_messages.append(message)

        # Find the most recent messages if they exist
        most_recent_byroad_message = valid_byroad_messages[-1] if valid_byroad_messages else None
        most_recent_onroad_message = valid_onroad_messages[-1] if valid_onroad_messages else None
        most_recent_response_message = valid_response_messages[-1] if valid_response_messages else None
        most_recent_response_message2 = valid_response_messages2[-1] if valid_response_messages2 else None
        most_recent_cancel_message = valid_cancel_messages[-1] if valid_cancel_messages else None

        return most_recent_byroad_message, valid_onroad_messages, most_recent_response_message, most_recent_response_message2, most_recent_cancel_message
    else:
        return None, None, None  # No valid SMS data found
    
def extract_locations(byroad_phone_no, byroad_message):
    if byroad_message:
        match1 = re.search(r"Byroad @(.+) @(.+)(?: #(\d+))?", byroad_message)
        match2 = re.search(r"Byroad @(.+) @(.+)", byroad_message)

        if match1:
            from_location = match1.group(1).strip()
            to_location = match1.group(2).strip()
            return from_location, to_location
        elif match2:
            from_location = match2.group(1).strip()
            to_location = match2.group(2).strip()
            return from_location, to_location
        else: 
            send_twilio_message(byroad_phone_no, "Hey that's an invalid format.\n "+"Follow the format below:\n"+"'Byroad @fromlocation @tolocation'")

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
        #send_twilio_message(byroad_phone, "Hey that's an invalid format.\n "+"Follow the format below:\n"+"'Byroad @fromlocation @tolocation'\n"+"Or try changing the addresses with some other landmark.")

        return None
    
def calculate_fare(distance_text, price_per_km):
    try:
        condition2 = True
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
        #send_twilio_message(byroad_phone, "Hey that's an invalid format.\n "+"Follow the format below:\n"+"'Byroad @fromlocation @tolocation'")

        return None
    
def extract_phone_number(byroad_message):
    if byroad_message:
        match1 = re.search(r"Byroad @.+ @.+ #(\d+)", byroad_message)
        match2 = re.search(r"Byroad @(.+) @(.+)", byroad_message)

        if match1:
        
            return "+91" + match1.group(1).strip()
        elif match2:
            sender_match = re.search(r"address=(\+\d+)", byroad_message)
            if sender_match:
                phone_number = sender_match.group(1).strip()
                
                return phone_number
        #else : 
            #send_twilio_message(byroad_phone, "Hey that's an invalid format.\n "+"Follow the format below:\n"+"'Byroad @fromlocation @tolocation'")

                

    return None

def extract_yeah_number(yeah_message):
    if yeah_message:
        # Define a regular expression pattern for extracting the number after '@'
        pattern = re.compile(r"Ok @(\d+)")

        match = pattern.search(yeah_message)
        if match:
            extracted_number = match.group(1).strip()
            return extracted_number
        #else:
         #send_twilio_message(byroad_phone, "Hey that's an invalid format.\n "+"Follow the format below:\n"+"'Byroad @fromlocation @tolocation'")


    return None
def send_twilio_message(to_phone_number, long_message):
    # Your Twilio Account SID, Auth Token, and Twilio phone number
    account_sid = 'AC1d0e1365cd6491e9f047b230e42005d6'
    auth_token = '73bdbef90093e3ff13ee9fcd9d3e1fc4'
    twilio_phone_number = '+13345184088'

    # Initialize the Twilio client
    client = Client(account_sid, auth_token)

    # Split the long message into segments (160 characters each)
    segments = [long_message[i:i+160] for i in range(0, len(long_message), 160)]

    try:
        # Send each segment as a separate Twilio message
        for i, segment in enumerate(segments, start=1):
            message = client.messages.create(
                body=segment,
                from_=twilio_phone_number,
                to=to_phone_number
            )
            print(f"Message segment {i} sent to {to_phone_number} SID: {message.sid}")

    except Exception as e:
        # Print an error message if sending fails
        print(f"Error sending message to {to_phone_number}: {str(e)}")



def extract_response_phone_number(response_message):
    if response_message:
        match = re.search(r"address=(\+\d+)", response_message)
        if match:
            return match.group(1).strip()
        #else:
             #send_twilio_message(byroad_phone, "Hey that's an invalid format.\n "+"Follow the format below:\n"+"'Byroad @fromlocation @tolocation'")

    return None

def extract_onroad_phone_number(onroad_message):
    if onroad_message:
        match = re.search(r"Onroad &(.+) #(\d+)", onroad_message)
        if match:
            phone_number = match.group(2).strip()
            return "+91" + phone_number
        #else:
            #send_twilio_message(byroad_phone, "Hey that's an invalid format.\n "+"Follow the format below:\n"+"'Byroad @fromlocation @tolocation'")

    return None

def extract_onroad_info(onroad_message):
    if onroad_message:
        # Define a regular expression pattern for extracting vehicle number plate and phone number
        pattern = re.compile(r"Onroad &(.+) #(\d+)")

        match = pattern.search(onroad_message)
        if match:
            vehicle_number_plate = match.group(1).strip()
            phone_number = match.group(2).strip()

            # Assuming the phone number is in the format '+91XXXXXXXXXX'
            formatted_phone_number = "+91" + phone_number

            return formatted_phone_number, vehicle_number_plate
        #else:
            #send_twilio_message(byroad_phone, "Hey that's an invalid format.\n "+"Follow the format below:\n"+"'Byroad @fromlocation @tolocation'")


    return None, None
def convert_duration_text_to_minutes(duration_text):
    match = re.match(r'(\d+)\s*(min|min\s*.)?', duration_text)
    
    if match:
        numeric_part = match.group(1)
        if numeric_part:
            return int(numeric_part)
    
    return 0

def ask_to_proceed(new_byroad, byroad_phone_no, total_fare_price, ttc, from_location, to_location) :
    
    #send_twilio_message(byroad_phone_no, "Unfortunately, we do not offer rides for short distances.\n However, we can always consider distances greater than 6 km.")    
        statement1, _, _,= statements(total_fare_price, from_location, to_location, ttc)
        send_twilio_message(byroad_phone_no, statement1)
        question_timestamp = time.time()
        question_datetime = datetime.now()

        
        while time.time() - question_timestamp < 60: 
            print("hi")
            byroad_message, onroad_message, _, response_message, _ = read_recent_sms(data)
            byroad_message_timestamp = datetime.now()
            read_recent_sms(data)
            if byroad_message and byroad_message != new_byroad:
                program_path = "savfinal.py"

                process = subprocess.Popen(['python', program_path])
            response_phone_number = extract_response_phone_number(response_message)
            byroad_phone_number = extract_phone_number(new_byroad)
            if response_phone_number == byroad_phone_number:
                if response_message is not None:
                    print("response message")
                    response_parts = response_message.split(',')
                    if len(response_parts) >= 2:
                        try:
                            print("present")
                            response_timestamp = int(response_parts[1].split('=')[1].strip())
                            response_datetime = datetime.fromtimestamp(response_timestamp / 1000.0)
                            in_minutes = convert_duration_text_to_minutes(ttc)
                            print(response_datetime, question_datetime)
                            if response_datetime > question_datetime:
                                with open('replies.txt', 'a') as file:
                                 file.write(from_location+" "+to_location+""+response_phone_number+str(response_datetime)+"\n")
                                print("present")
                                onroad_phone_nos, onroad_messages = process_onroad(from_location, to_location, response_phone_number, response_datetime, in_minutes, data)
                                print(onroad_phone_nos)
                                ask_to_proceed2(onroad_phone_nos, from_location, to_location, total_fare_price, onroad_messages, byroad_phone_no, ttc, new_byroad)
                                return response_message.lower()
                        except (ValueError, IndexError):
                            print("Error extracting or converting repsonse timestamp.")
                            #send_twilio_message(byroad_phone_no, "Hey that's an invalid format.\n "+"Follow the format below:\n"+"'Byroad @fromlocation @tolocation'")

            time.sleep(10)
        _, _, statement3 =  statements(total_fare_price, from_location, to_location, ttc)
        send_twilio_message(byroad_phone_no, statement3)

   
        return None
    
    
def ask_to_proceed2(onroad_phone_nos, from_location, to_location, total_fare_price, onroad_messages, byroad_phone_no, ttc, new_byroad):
    _, statement2, _ = statements(total_fare_price, from_location, to_location, ttc)
    for k in range(len(onroad_phone_nos)):
        send_twilio_message(onroad_phone_nos[k], statement2)
    #make_twilio_call(onroad_phone_nos, '<Response><Say>We have got a customer, just check your message box.</Say><Hangup/></Response>')
    question_timestamp1 = time.time()
    question_datetime1 = datetime.now()
    condition1 = False

    while time.time() - question_timestamp1 < 60 :
        byroad_message1, onroad_message, response_message1, _, _= read_recent_sms(data)
        read_recent_sms(data)
        if byroad_message1 and byroad_message1 != new_byroad:
                                        program_path = "savfinal.py"

                                        process = subprocess.Popen(['python', program_path])
        condition = False
        #if
        response_message_phone_number1 = extract_response_phone_number(response_message1)

        for i in range(len(onroad_phone_nos)):
            if onroad_phone_nos[i] == response_message_phone_number1:
                condition = True
        if condition == True:
                print("present1")
                if response_message1 is not None:
                    print("present2")
                    response_interval = extract_yeah_number(response_message1)
                    response_parts1 = response_message1.split(',')

                    if len(response_parts1) >= 2:
                        try:
                            print("present3")
                            response_timestamp1 = int(response_parts1[1].split('=')[1].strip())
                            response_datetime1 = datetime.fromtimestamp(response_timestamp1 / 1000.0)
                            if response_datetime1 > question_datetime1 :
                                condition1 = True

                                print("present4")
                                send_twilio_message(response_message_phone_number1, f"Passenger's Contact : {byroad_phone_no}")
                                for j in range(len(onroad_messages)):
                                    if response_message_phone_number1 == extract_onroad_phone_number(onroad_messages[j]):
                                        corresponding_response_message = onroad_messages[j]
                                corresponding_response_message_phoneno, corresponding_response_message_noplate = extract_onroad_info(corresponding_response_message)
                                statement4, _, _, _, _ = statements1(corresponding_response_message_noplate, corresponding_response_message_phoneno, response_interval)
                                send_twilio_message(byroad_phone_no, statement4)
                                cancellation_timestamp = datetime.now()
                                while cancellation_timestamp < (cancellation_timestamp + timedelta(minutes=int(response_interval))):
                                    byroad_recent, _, _, _, cancellation_response = read_recent_sms(data)
                                    cancellation_response_phone_no = extract_response_phone_number(cancellation_response)
                                    read_recent_sms(data)
                                    if byroad_recent and byroad_recent != new_byroad:
                                        program_path = "savfinal.py"

                                        process = subprocess.Popen(['python', program_path])
                                    
                                    if cancellation_response_phone_no == byroad_phone_no:
                                        if cancellation_response is not None :
                                            cancellation_response_parts = cancellation_response.split(',')
                                            if len(cancellation_response_parts) >= 2 :
                                                try:
                                                    cancellation_response_timestamp = int(cancellation_response_parts[1].split('=')[1].strip())
                                                    cancellation_response_datetime = datetime.fromtimestamp(cancellation_response_timestamp / 1000.0)
                                                    if cancellation_response_datetime > cancellation_timestamp:
                                                        _, statement5, statement6, _, _ = statements1(corresponding_response_message_noplate, corresponding_response_message_phoneno, response_interval)
                                                        
                                                        send_twilio_message(byroad_phone_no, statement5)
                                                        send_twilio_message(corresponding_response_message_phoneno, statement6)
                                                        break

                                                except (ValueError, IndexError):
                                                    print("Error extracting or converting cancellation_response_timestamp")
                                                    #send_twilio_message(byroad_phone_no, "Hey that's an invalid format.\n "+"Follow the format below:\n"+"'Byroad @fromlocation @tolocation'")

                                        time.sleep(10)
                                if cancellation_response is None:
                                 _, _, _, statement7, _ = statements1(corresponding_response_message_noplate, corresponding_response_message_phoneno, response_interval)
                                 send_twilio_message(byroad_phone_no, statement7)


                                return response_message1.lower()
                        except (ValueError, IndexError):
                            print("Error extracting or converting response timestamp.")
                            #send_twilio_message(byroad_phone_no, "Hey that's an invalid format.\n "+"Follow the format below:\n"+"'Byroad @fromlocation @tolocation'")

        time.sleep(10)
    if condition1 == False:
     send_twilio_message(byroad_phone_no, "Sorry! No rides available near you at this moment. Thank you for considering us.")

    return None
     

def process_byroad(api_key, price_per_km):
    most_recent_byroad = None
    while True:
        new_byroad, _, _, _, _ = read_recent_sms(data)
        
        if new_byroad and new_byroad != most_recent_byroad:
            try:
                with open('mess.txt','r') as file:
                    lines = file.readlines()
                    found = True

                    for line_number, line in enumerate(lines, start = 1):
                        if new_byroad in line:
                            found = False
                    if found == True:
                        with open('mess.txt', 'a') as file:
                         file.write(new_byroad+"\n")
                        print(new_byroad)
                        phone_no = extract_phone_number(new_byroad)

                        from_location, to_location = extract_locations(phone_no, new_byroad)
                        print(from_location, to_location)
                        if from_location and to_location:

                            distance_text = calculate_distance(from_location, to_location, api_key)
                            if distance_text:
                                fare_price= calculate_fare(distance_text, price_per_km)
                                ttc = calculate_eta(from_location, to_location, api_key)
                                ask_to_proceed(new_byroad, phone_no, fare_price, ttc, from_location, to_location)

                        most_recent_byroad = new_byroad
                    time.sleep(30)
            except FileNotFoundError:
                print(f'The file messages does not exist.')
               # send_twilio_message(phone_no, "Hey that's an invalid format.\n "+"Follow the format below:\n"+"'Byroad @fromlocation @tolocation'")

            except Exception as e:
                print(f'An error occured:{e}')
               # send_twilio_message(phone_no, "Hey that's an invalid format.\n "+"Follow the format below:\n"+"'Byroad @fromlocation @tolocation'")


def process_onroad(from_location, to_location, response_phone_no, response_datetime, ttc, data):
    onroad_messages = []
    phone_nos = []
    _, onroad_messages, _, _, _ = read_recent_sms(data)
    recent_onroad = from_location+" "+to_location+" "+response_phone_no+" "+str(response_datetime)
    
    with open('replies.txt','r') as file:
                    lines = file.readlines()
                    found = True

                    for line_number, line in enumerate(lines, start = 1):
                        
                         if recent_onroad in line and datetime.now() < response_datetime + timedelta(minutes=ttc):  
                            found = False

    for i in range(len(onroad_messages)):
        
            
        phone_nos.append(extract_onroad_phone_number(onroad_messages[i]))
    if found == False:
        phone_nos.remove(response_phone_no)

    return phone_nos, onroad_messages

if __name__ == "__main__":
    app.run()
    google_maps_api_key = 'AIzaSyC3TDYhGNQQcRkOxs7T1iTSLoOE5mIU-sE'
    price_per_km = 20
    process_byroad(google_maps_api_key, price_per_km) 
                        

                                       




C:\Users\Aaryan\Downloads