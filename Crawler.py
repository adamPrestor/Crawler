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

    # parsed_url = urlparse(INIT_FRONTIER[0])
    # domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)
    # robots = urllib.parse.urljoin(domain, "robots.txt")
    # print(robots)

    # rp = urllib.robotparser.RobotFileParser(robots)
    # rp.read()

    # db.add_to_frontier(INIT_FRONTIER[0])
    # db.add_to_frontier(INIT_FRONTIER[1])

    # db.add_link(INIT_FRONTIER[0], INIT_FRONTIER[1])
    # db.get_frontier()

    # request = urllib.request.Request(
    #     INIT_FRONTIER[0],
    #     headers={'User-Agent': 'fri-ieps-TEST'}
    # )

    # with urllib.request.urlopen(request) as response:
    #     html = response.read().decode("utf-8")
    #     # print(f"Retrieved Web content: \n\n'\n{html}\n'")