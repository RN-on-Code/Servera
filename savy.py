import requests
import re
import datetime
from datetime import datetime, timedelta
def calculate_eta(origin = "uruli kanchan", destination="Nigdi", api_key='AIzaSyC3TDYhGNQQcRkOxs7T1iTSLoOE5mIU-sE'):
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
def convert_duration_text_to_minutes(duration_text = calculate_eta()):
    match = re.match(r'(\d+)\s*(min|min\s*.)?', duration_text)
    
    if match:
        numeric_part = match.group(1)
        print(numeric_part)
        if numeric_part:
            #print(numeric_part)
            return int(numeric_part)
    
    return 0
response_datetime = datetime.now()
total = response_datetime+timedelta(minutes=convert_duration_text_to_minutes())
print(total)