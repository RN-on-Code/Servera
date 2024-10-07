from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/sms", methods=['POST'])
def sms_reply():
    # Get the incoming message
    incoming_msg = request.form.get('Body')

    # Create a Twilio response object
    resp = MessagingResponse()

    # Customize the reply message
    if 'hello' in incoming_msg.lower():
        reply = "Hello! How can I help you today?"
    else:
        reply = "Thank you for your message!"

    # Add the reply message to the response
    resp.message(reply)

    return Response(str(resp), mimetype="application/xml")

if __name__ == "__main__":
    app.run(debug=True)
