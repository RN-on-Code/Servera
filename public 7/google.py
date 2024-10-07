from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route('/search', methods=['POST'])
def search():
    query = request.json['query']
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return jsonify({'result': response.text})
    else:
        return jsonify({'error': 'Failed to fetch search results'}), 500

if __name__ == '__main__':
    app.run(debug=True)
