import requests 
def calculate_distance(origin='Nilesh Park Malwadi Hadapsar', destination='Anna Bhau Sathe Vasahat Nigdi', api_key='AIzaSyC3TDYhGNQQcRkOxs7T1iTSLoOE5mIU-sE'):
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
distance = calculate_distance()
print(distance)