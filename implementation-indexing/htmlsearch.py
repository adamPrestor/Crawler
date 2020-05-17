import sys
import time

from pathlib import Path
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

from indexing import index_page
from preprocessing import preprocessing
from sqlsearch import process_results, output_string


def run_search(root_dir, query):
    results = []
    root = Path(root_dir)

    filepaths = list(root.rglob('*.html'))
    for filepath in tqdm(filepaths):
        # Read page
        with open(filepath, 'r') as file:
            html_data = file.read()

        # Compute inverted index for the page
        word_list, frequencies, indexes = index_page(html_data)
        document = str(filepath.relative_to(root))

        indices = []
        freq = 0
        for word in query:
            freq += frequencies.get(word, 0)
            indices += indexes.get(word, [])

        if freq:
            results.append((freq, indices, document))

    results.sort(key=lambda e: (e[0], e[1]), reverse=True)

    return results


def main(raw_query, limit):
    dirname = Path(__file__).parent
    data_dir = dirname / 'data'

    results_considered = int(limit)
    start_time = time.time()

    # preprocess the query
    query = preprocessing.preprocess(raw_query)

    results = run_search(data_dir, query)

    time_elapsed = time.time() - start_time

    to_process = results[:min(results_considered, len(results))]

    output = process_results(to_process, data_dir)

    return output_string(raw_query, time_elapsed, output)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
