import urllib
import urllib.request
import urllib.robotparser
import urllib.parse
from urllib.parse import urlparse

import Database as db


INIT_FRONTIER = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.gov.si/",
    "https://evem.gov.si/",
    "https://e-uprava.gov.si/",
    "https://e-prostor.gov.si/",
]


def crawl():
    # TODO: do the thread locking when implementing multithread crawlers
    db.get_frontier()


if __name__ == '__main__':

    parsed_url = urlparse(INIT_FRONTIER[0])
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)
    robots = urllib.parse.urljoin(domain, "robots.txt")
    print(robots)

    rp = urllib.robotparser.RobotFileParser(robots)
    rp.read()

    db.add_to_frontier(INIT_FRONTIER[0])
    db.add_to_frontier(INIT_FRONTIER[1])

    db.add_link(INIT_FRONTIER[0], INIT_FRONTIER[1])
    db.get_frontier()

    request = urllib.request.Request(
        INIT_FRONTIER[0],
        headers={'User-Agent': 'fri-ieps-TEST'}
    )

    with urllib.request.urlopen(request) as response:
        html = response.read().decode("utf-8")
        # print(f"Retrieved Web content: \n\n'\n{html}\n'")
