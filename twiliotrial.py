from twilio.rest import Client

# Twilio credentials (replace with your own)
account_sid = 'AC1d0e1365cd6491e9f047b230e42005d6'
auth_token = '73bdbef90093e3ff13ee9fcd9d3e1fc4'
client = Client(account_sid, auth_token)

# Send an SMS
message = client.messages.create(
    body='Hello! This is a test message from Twilio.',
    from_='+13345184088',
    to='+919970638387'
)

print(f"Message sent with SID: {message.sid}")
