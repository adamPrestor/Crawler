# Web Crawler

## Setup


1. Install requirements.

```bash
pip install -r requirements.txt
```

2. Setup database with the [`crawldb.sql`](crawldb.sql) script
3. Edit the [`settings.py`](crawler/settings.py) to specify the driver location, database credentials, and defaults
4. Start the crawler

```bash
python -m crawler.Crawler
```

Optionally you can specify the number of workers by using the flag. Default number of workers is configured in settings.

```bash
python -m crawler.Crawler -n 6
```

## Report and analysis

The report is available [here](#).

The code that was used to produce plots and additional analysis is available in [this jupyter notebook](analysis/analysis.ipynb).