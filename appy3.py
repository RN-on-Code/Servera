import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r'C:/Users/Aaryan/vs.material/my-application-7a202-firebase-adminsdk-ttyry-60e09e525c.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://my-application-7a202-default-rtdb.firebaseio.com/'  # Ensure this URL is correct
})
# Test accessing the root of your database

# Reference to 'messages' node
ref = db.reference('messages')

# Attempt to read from the 'messages' node
try:
    sms_messages = ref.get()
    if sms_messages is None:
        print("No data found at 'messages'.")
    else:
        print(sms_messages)
except Exception as e:
    print(f"Error retrieving messages: {e}")
