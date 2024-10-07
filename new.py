import nltk
from nltk import pos_tag, word_tokenize

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

def extract_nouns(sentence):
    nouns = []
    words = word_tokenize(sentence)
    tagged_words = pos_tag(words)
    for word, pos in tagged_words:
        if pos.startswith('NN'):
            nouns.append(word)
    return nouns

def main():
    sentence = "delete the word mine and write there wine instead"
    nouns = extract_nouns(sentence)
    print("Nouns in the sentence:", nouns)

if __name__ == "__main__":
    main()
