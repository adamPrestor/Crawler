import sys
import time
from itertools import chain

from bs4 import BeautifulSoup
from pathlib import Path
from nltk import word_tokenize
from tqdm.auto import tqdm

from stopwords import stop_words_slovene
from preprocessing import preprocessing
import database as db


def output_string(raw_query, time_elapsed, outputs):
    left_col = 11
    mid_col = 45
    right_col = 70

    string = f'Results for a query: \"{raw_query}\"\n\n' \
             f'\tResults found in {time_elapsed:.2f}ms\n\n' \
             f'\t{"Frequencies".ljust(left_col)} {"Document".ljust(mid_col)} {"Snippet".ljust(right_col)}\n' \
             f'\t{"-"*left_col} {"-"*mid_col} {"-"*right_col}\n'

    for out in outputs:
        string += f'\t{str(out[0]).ljust(left_col)} {str(out[1]).ljust(mid_col)} {str(out[2]).ljust(right_col)}\n'

    return string


def group_runs(li, tolerance=1):
    out = []
    last = li[0]
    for x in li:
        if x-last > tolerance:
            yield out
            out = []
        out.append(x)
        last = x
    yield out


def make_snippet(html_data, indexes):
    snip = f""
    for group in indexes:
        for i in group:
            snip += f"{str(html_data[i])} "
        snip += '... '

    return snip


def process_results(results: list, html_path):
    out = []
    for res in results:
        pos = res[1]
        document = res[2]
        filepath = html_path / document

        with filepath.open() as file:
            html_data = file.read()

        soup = BeautifulSoup(html_data, features='html.parser')

        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.extract()

        # Get only text from page and preprocess it
        text = soup.get_text(separator=' ')
        tokens = preprocessing.preprocess(text, raw=True, keep_stop_words=True)
        # print(len(tokens), len(word_tokenize(text)))

        document_length = len(tokens)

        outtake = list(group_runs(list(sorted(set(chain.from_iterable([list(range(max(0, x-3), min(x+4, document_length))) for x in pos[:100]]))))))

        snippet = make_snippet(tokens, outtake)

        # print(pos)
        # print(outtake)
        # print(snippet[:250])
        out.append((res[0], res[2], snippet[:250]))

    return out


def sqlite_search(query):
    # get all the documents in the dataset
    docs = db.get_all_documents()

    # debug prints
    # print(len(docs), docs)
    # print(query)

    results = []

    # cycle through the documents, get frequency and positions
    for doc in tqdm(docs):
        freq, positions = db.get_frequency_and_position(query, doc)

        if freq:
            results.append((freq, positions, doc[0]))

    results.sort(key=lambda e: (e[0], e[1]), reverse=True)

    return results


def main(raw_query, limit):
    results_considered = int(limit)
    start_time = time.time()

    # preprocess the query
    query = preprocessing.preprocess(raw_query)

    results = sqlite_search(query)

    time_elapsed = time.time() - start_time

    to_process = results[:min(results_considered, len(results))]

    html_path = Path(__file__).parent / 'data'
    output = process_results(to_process, html_path)

    return output_string(raw_query, time_elapsed, output)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
