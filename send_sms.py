import vonage

# Initialize the Vonage client with your API key and secret
client = vonage.Client(key='3a1666f1', secret='HVkgJV5OiN4h5HDP')
#client = vonage.Client(key="3a1666f1", secret="HVkgJV5OiN4h5HDP")
sms = vonage.Sms(client)

# Send an SMS
responseData = sms.send_message(
    {
        "from": "Vonage APIs",
        "to": "+919970638387",
        "text": "A text message sent using the Nexmo SMS API",
    }
)

if responseData["messages"][0]["status"] == "0":
    print("Message sent successfully.")
else:
    print(f"Message failed with error: {responseData['messages'][0]['error-text']}")