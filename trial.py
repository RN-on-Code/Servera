from twilio.rest import Client

# Your Twilio account SID, Auth Token, and Twilio phone number
account_sid = 'AC9732b9a5f922bf227132bde7205e6c01'
auth_token = '4e43c05500ffc7faa6d50bf93a5c0d4f'
twilio_phone_number = '+13346001562'

# The recipient's phone number
recipient_phone_number = '+919970638387'

# Create a Twilio client
client = Client(account_sid, auth_token)

# Set the message to be spoken
message_to_speak = "Hello! This is a sample message from Twilio."

# Create TwiML with the message
twiml = f"""
<Response>
    <Say>{message_to_speak}</Say>
</Response>
"""

# Make a phone call with the specified TwiML
call = client.calls.create(
    to=recipient_phone_number,
    from_=twilio_phone_number,
    twiml=twiml
)

print(f"Call SID: {call.sid}")
