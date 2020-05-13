from bs4 import BeautifulSoup

from preprocessing import preprocessing


def index_page(html_data):
    """ Indexes a single HTML page. """

    soup = BeautifulSoup(html_data, features='html.parser')

    # Remove scripts and styles
    for script in soup(["script", "style"]):
        script.extract()

    # Get only text from page and preprocess it
    text = soup.get_text(separator=' ')
    tokens = preprocessing.preprocess(text)

    # Unique words
    word_list = set(tokens)

    # Get frequencies and indices
    frequencies = {word: 0 for word in word_list}
    indexes = {word: [] for word in word_list}
    for i, word in enumerate(tokens):
        frequencies[word] += 1
        indexes[word].append(i)


    return word_list, frequencies, indexes

