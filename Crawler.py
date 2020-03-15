import urllib
import urllib.request
import urllib.robotparser
import urllib.parse
from urllib.parse import urlparse
from multiprocessing import Queue

import Database as db
from worker import URLWorker


NUM_WORKERS = 5
INIT_FRONTIER = [
    "https://www.gov.si/",
    "https://evem.gov.si/",
    "https://e-uprava.gov.si/",
    "https://e-prostor.gov.si/",
]


def crawl():

    frontier_queue = Queue()
    response_queue = Queue()

    for i in range(NUM_WORKERS):
        URLWorker(frontier_queue, response_queue).start()

    # Add initial frontier urls
    for url in INIT_FRONTIER:
        frontier_queue.put(url)

    # Processing loop (recieve urls, add to frontier)
    while True:
        try:
            links = response_queue.get(timeout=10)

            for url in links:
                # TODO: check if already visited, etc.
                frontier_queue.put(url)

        except queue.Empty:
            break

    # Send exit signal to workers
    for i in range(NUM_WORKERS):
        frontier_queue.put(None)


if __name__ == '__main__':

    crawl()
