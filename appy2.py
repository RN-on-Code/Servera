import re
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase app (ensure to replace 'path/to/your-firebase-credentials.json' with your actual credentials file)
cred = credentials.Certificate('my-application-7a202-firebase-adminsdk-ttyry-60e09e525c.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://my-application-7a282.firebaseio.com/'  # Replace with your Firebase Realtime Database URL
})

def read_recent_sms():
    # Reference to the messages node in Firebase
    ref = db.reference('messages')
    sms_messages = ref.get()

    if sms_messages:
        # Regex patterns for matching Byroad and Onroad messages
        byroad_pattern1 = re.compile(r"Byroad @(.+) @(.+)(?: #(\d+))?")
        byroad_pattern2 = re.compile(r"Byroad @(.+) @(.+)")
        onroad_pattern = re.compile(r"Onroad &(.+) #(\d+)")
        response_pattern = re.compile(r"Ok @(.+)", re.IGNORECASE)
        response_pattern2 = re.compile(r"(Yeah)", re.IGNORECASE)
        cancel_message_pattern = re.compile(r"Byroad @Cancel")

        # Extract valid Byroad, Onroad, and response messages
        valid_byroad_messages = [msg for key, msg in sms_messages.items() if byroad_pattern1.search(msg['message']) or byroad_pattern2.search(msg['message'])] 
        valid_onroad_messages = [msg for key, msg in sms_messages.items() if onroad_pattern.search(msg['message'])]
        valid_response_messages = [msg for key, msg in sms_messages.items() if response_pattern.search(msg['message'])]
        valid_response_messages2 = [msg for key, msg in sms_messages.items() if response_pattern2.search(msg['message'])]
        valid_cancel_message = [msg for key, msg in sms_messages.items() if cancel_message_pattern.search(msg['message'])]

        # Find the most recent Byroad, Onroad, and response messages
        most_recent_byroad_message = valid_byroad_messages[-1] if valid_byroad_messages else None
        most_recent_onroad_message = valid_onroad_messages[-1] if valid_onroad_messages else None
        most_recent_response_message = valid_response_messages[-1] if valid_response_messages else None
        most_recent_response_message2 = valid_response_messages2[-1] if valid_response_messages2 else None
        most_recent_cancel_message = valid_cancel_message[-1] if valid_cancel_message else None

        return most_recent_byroad_message, valid_onroad_messages, most_recent_response_message, most_recent_response_message2, most_recent_cancel_message
    else:
        return None, None, None, None, None  # No SMS messages found

# Call the function to test
recent_byroad, valid_onroad, recent_response, recent_response2, recent_cancel = read_recent_sms()
print("Most Recent Byroad:", recent_byroad)
print("Valid Onroad Messages:", valid_onroad)
print("Most Recent Response:", recent_response)
print("Most Recent Response 2:", recent_response2)
print("Most Recent Cancel Message:", recent_cancel)
