import re
from nltk import word_tokenize
import lemmagen
from lemmagen.lemmatizer import Lemmatizer

from stopwords import stop_words_slovene

class Preprocessing:
    def __init__(self):
        self.lemmatizer = Lemmatizer(dictionary=lemmagen.DICTIONARY_SLOVENE)
        self.punc_regex = re.compile(r'^[^0-9a-zA-Z]+$')

    def preprocess(self, text):
        # Tokenize
        tokens = word_tokenize(text)

        # Lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]

        # Convert to lowercase
        tokens = [t.lower() for t in tokens]

        # Remove stopwords and punctuations
        tokens = [t for t in tokens if t not in stop_words_slovene and not self.punc_regex.match(t)]

        return tokens

preprocessing = Preprocessing()
