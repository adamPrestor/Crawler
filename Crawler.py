import logging
import urllib
import urllib.request
import urllib.robotparser
import urllib.parse
from urllib.parse import urlparse
from multiprocessing import Queue, Lock

import Database as db
from worker import URLWorker
import settings


def crawl():
    lock = Lock()

    db.init_frontier()

    # Add initial frontier urls
    for url in settings.INIT_FRONTIER:
        db.add_to_frontier(url)

    for i in range(settings.DEFAULT_NUM_WORKERS):
        URLWorker(lock, i).start()


if __name__ == '__main__':
    logging.basicConfig(filename='crawler.log', level=logging.NOTSET, format='%(levelname)s:%(asctime)s: %(message)s')
    logging.critical("Crawler started.")
    crawl()
