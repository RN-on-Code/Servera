from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Hello, this is a basic Flask web app!</h1><p>Ngrok is working!</p>'

if __name__ == '__main__':
    app.run(port=5000)  # You can change the port if needed
