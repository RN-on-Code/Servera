from flask import Flask, request
from twilio.rest import Client

# Twilio credentials
account_sid = 'ACa556366ea31da529c3e6c5a466864ef2'
auth_token = 'ed7ccffccfaee6671973844c777209ca'
twilio_phone_number = '+16672880621'  #Your Twilio phone number

# Flask web server
app = Flask(__name__)

# Twilio callback endpoint
@app.route('/twilio/callback', methods=['POST'])
def handle_twilio_callback():
    # Extract relevant information from the incoming request
    message_sid = request.form['MessageSid']
    from_number = request.form['From']
    body = request.form['Body']

    # Process the information as needed (e.g., store it in a database)

    return 'OK'  # Respond to Twilio with a 200 OK

# Send an SMS using Twilio
def send_sms(to_number, message_body):
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message_body,
        from_=twilio_phone_number,
        to=to_number,
        status_callback='https://your-server-url.com/twilio/callback'
    )

    return message.sid

if __name__ == '__main__':
    # Replace 'https://your-server-url.com' with the actual URL where your server is accessible
    server_url = 'https://demo.twilio.com/welcome/sms/reply/'
    
    # Start the Flask web server in a separate thread
    import threading
    threading.Thread(target=app.run, kwargs={'debug': True}).start()

    # Example: Send an SMS
    recipient_number = '+919970638387'  # Replace with the recipient's phone number
    message_text = 'Hello, this is a test message!'
    
    # Send the SMS
    message_sid = send_sms(recipient_number, message_text)

    print(f'SMS sent! Message SID: {message_sid}')
