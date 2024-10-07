from flask import Flask, request

app = Flask(__name__)

@app.route('/receive_sms', methods=['POST'])
def receive_sms():
    data = request.get_json()
    print(f"Message received: {data}")
    return "Message received", 200

if __name__ == '__main__':
    app.run()
