# backend_server.py

from flask import Flask, request, jsonify
from nltk.tokenize import word_tokenize
from nltk import pos_tag

app = Flask(__name__)

@app.route('/extract-nouns', methods=['POST'])
def extract_nouns():
    data = request.json
    text = data['text']
    
    # Tokenize the text
    tokens = word_tokenize(text)
    
    # Perform part-of-speech tagging
    tagged_words = pos_tag(tokens)
    
    # Filter nouns (NN and NNS)
    nouns = [word for word, tag in tagged_words if tag in ['NN', 'NNS']]
    
    return jsonify({'nouns': nouns})

if __name__ == '__main__':
    app.run(debug=True)
