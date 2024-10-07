from twilio.rest import Client

# Your Twilio Account SID and Auth Token
account_sid = 'ACa556366ea31da529c3e6c5a466864ef2'
auth_token = 'ed7ccffccfaee6671973844c777209ca'

# Create a Twilio client
client = Client(account_sid, auth_token)

# Receiver's phone number (include the country code)
receiver_number = '+919970638387'

# Your Twilio phone number (you can find this in your Twilio console)
twilio_number = '+16672880621'

# Your long message
long_message = """
This is a long message. Twilio will automatically split it into multiple
SMS messages if it exceeds the maximum length allowed (usually 160 characters
per message). The recipient will see a concatenated version of these messages.
"""

# Send the message
message = client.messages.create(
    body=long_message,
    from_=twilio_number,
    to=receiver_number
)

# Print the SID (Unique identifier) of the sent message
print(f"Message SID: {message.sid}")
