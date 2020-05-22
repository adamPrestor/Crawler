# Data indexing

* HTML webpages inverted index generation
* Data retrieval using queries

The report is available [here](report-indexing.pdf).

## Setup

The dependencies for the project are listed in the (`requirements.txt`)[implementation-indexing/requirements.txt] file.

```bash
pip install -r implementation-indexing/requirements.txt
```

## Data retrieval

Data retrieval can be done using the `run-sql-search.py` or `run-basic-search.py` scripts.


`run-sql-search.py` uses the index built and saved to the SQLite dataset.

```bash
# python implementation-indexing/run-sql-search.py QUERY
python implementation-indexing/run-sql-search.py dejavnost
python implementation-indexing/run-sql-search.py "Sistem SPOT"
```

`run-basic-search.py` processes the files sequentially and merges the results.

```bash
# python implementation-indexing/run-basic-search.py QUERY
python implementation-indexing/run-basic-search.py dejavnost
python implementation-indexing/run-basic-search.py "Sistem SPOT"
```

## Webpage indexing

WARNING: This will overwrite the provided index database (`inverted-index.db`).

Webpages to index should be put into the `implementation-indexing/data` folder.

An index of webpages can be then built using the (`indexing.py`)[implementation-indexing/indexing.py] script.

```bash
python implementation-indexing/indexing.py
```
