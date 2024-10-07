from twilio.rest import Client

# Your Twilio Account SID, Auth Token, and Twilio phone number
account_sid = 'ACa556366ea31da529c3e6c5a466864ef2'
auth_token = 'ed7ccffccfaee6671973844c777209ca'
twilio_phone_number = '+16672880621'
origin='Nilesh Park Malwadi Hadapsar'

# Recipient's phone number (make sure to include the country code, e.g., +1 for the United States)
recipient_phone_number = '+919970638387'

# Your message
message_body = "From: "+ str(origin)
# Initialize the Twilio client
client = Client(account_sid, auth_token)

# Send the message
message = client.messages.create(
    body=message_body,
    from_=twilio_phone_number,
    to=recipient_phone_number
)

# Print the SID (unique identifier) of the sent message
print(f"Message sent successfully! SID: {message.sid}")
print(len(message_body))
