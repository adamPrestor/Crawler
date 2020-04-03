import argparse
import logging
import urllib
import urllib.request
import urllib.robotparser
import urllib.parse
from urllib.parse import urlparse
from multiprocessing import Queue, Lock

from . import Database  as db
from .worker import URLWorker
from . import settings


def crawl(num_workers):
    lock = Lock()

    db.init_frontier()

    # Add initial frontier urls
    for url in settings.INIT_FRONTIER:
        db.add_to_frontier(url)

    for i in range(num_workers):
        URLWorker(lock, i).start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Configurable multithreaded web crawler.")
    parser.add_argument('--num_workers', '-n', type=int, default=settings.DEFAULT_NUM_WORKERS,
                        help=f'Number of parallel crawlers. Defaults to {settings.DEFAULT_NUM_WORKERS}')

    args = parser.parse_args()

    logging.basicConfig(filename='crawler.log', level=logging.WARNING, format='%(levelname)s:%(asctime)s: %(message)s')
    logging.critical("Crawler started.")
    crawl(args.num_workers)
