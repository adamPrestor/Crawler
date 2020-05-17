from pathlib import Path
from tqdm.auto import tqdm

import sqlsearch
import htmlsearch

queries = [
    "predelovalne dejavnosti",
    "trgovina",
    "social services",
    "socialno delo",
    "varovanje človekovih pravic",
    "seja državnega zbora",
]

output_folder = Path(__file__).parent / 'outputs'
limit = 6

for query in tqdm(queries):
    # do query for sql search
    out_file = output_folder / f'{query}-sql'
    string = sqlsearch.main(query, limit)
    with out_file.open('w') as f:
        f.write(string)

    # do query for sql search
    out_file = output_folder / f'{query}-raw'
    string = htmlsearch.main(query, limit)
    with out_file.open('w') as f:
        f.write(string)

