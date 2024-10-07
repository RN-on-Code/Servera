from twilio.rest import Client

def send_messages(account_sid, auth_token, twilio_phone_number, phone_numbers, message_body):
    # Create a Twilio client
    client = Client(account_sid, auth_token)

    # Send messages to each phone number
    for phone_number in phone_numbers:
        message = client.messages.create(
            body=message_body,
            from_=twilio_phone_number,
            to=phone_number
        )

        print(f'Message sent to {phone_number}. SID: {message.sid}')

# Example usage
if __name__ == "__main__":
    # Replace with your actual Twilio credentials and phone number
    account_sid = 'ACa556366ea31da529c3e6c5a466864ef2'
    auth_token = 'ed7ccffccfaee6671973844c777209ca'
    twilio_phone_number = '+16672880621'

    # List of phone numbers to send messages to
    phone_numbers = ['+918605040803', '+919970638387', '+918262934148', '+919518324339']

    # Message to be sent
    message_body = 'Thank you for considering us. So your total fare becomes . Should we proceed find you a ride? Reply (Yes) to proceed to +918888605312 else ignore.'

    # Call the function to send messages
    send_messages(account_sid, auth_token, twilio_phone_number, phone_numbers, message_body)
