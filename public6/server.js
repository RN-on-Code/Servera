fetch('/extract-nouns', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ text })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to fetch');
    }
    return response.json();
  })
  .then(data => {
    // Handle response data
  })
  .catch(error => {
    console.error('Error fetching data:', error);
  });
  

const express = require('express');
const natural = require('natural');
const app = express();

// Middleware to parse JSON
app.use(express.json());

// Endpoint to handle speech recognition
app.post('/extract-nouns', (req, res) => {
    const text = req.body.text;

    // Use natural language processing to extract nouns
    const tokenizer = new natural.WordTokenizer();
    const words = tokenizer.tokenize(text);
    const taggedWords = new natural.BrillPOSTagger().tag(words);
    const nouns = taggedWords.filter(word => word[1].startsWith('NN')).map(word => word[0]);

    // Send back the extracted nouns
    res.json({ nouns });
});

// Start the server
const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
