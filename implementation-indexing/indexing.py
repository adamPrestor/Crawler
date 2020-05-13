import os
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

from preprocessing import preprocessing
import database as db


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

def process_pages(root_dir):
    root = Path(root_dir)

    filepaths = list(root.rglob('*.html'))
    for filepath in tqdm(filepaths):
        # Read page
        with open(filepath, 'r') as file:
            html_data = file.read()

        # Compute inverted index for the page
        word_list, frequencies, indexes = index_page(html_data)
        document = str(filepath.relative_to(root))

        # Save to dataset
        db.insert_index(document, word_list, frequencies, indexes)


if __name__ == '__main__':
    dirname = Path(__file__).parent
    data_dir = dirname / 'data'

    process_pages(data_dir)
