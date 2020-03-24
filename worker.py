import re
import time
import requests
from datetime import datetime

from URL_parser import URLParser
from multiprocessing import Process

import Database as db

url_re = re.compile(r'\.gov.si?/')

class URLWorker(Process):
    """ Worker class. Retrieves and parses url and adds data to the dataset. """

    def __init__(self, lock, id):
        super().__init__()
        self.lock = lock
        self.id = id

    def run(self):
        while True:
            with URLParser() as parser:
                # Reads urls from queue until it receives the sentinel value of None
                print('I am here, doing nothing: ' + str(self.id))
                try:
                    # get the frontier out of the DB - FIFO style
                    self.lock.acquire()
                    page_id, url = db.get_frontier()
                    self.lock.release()

                    # TODO: check for the delay on the domain - db.get_domain_last_visit

                    # Head request to get status code and page type
                    head = requests.head(url, allow_redirects=True)
                    status_code = head.status_code

                    if status_code < 400:
                        content_type = head.headers['content-type']
                        if content_type.startswith('text/html'):
                            # If page is HTML then parse it
                            res = parser.parse_url(url)

                            # Write parsed data to dataset (update page)
                            db.page_content(page_id=page_id, url=url, html=res.html_content, page_type='HTML',
                                            status=status_code, at=res.access_time)

                            # add all the binary content type to link to the page
                            for binary in res.binary_links:
                                dtype = binary.split('.')[-1].upper()
                                # TODO: maybe get data type with HEAD request
                                db.add_page_data(page=page_id, data=binary, data_type=dtype)

                            # add image data from the page
                            for image in res.image_links:
                                pass

                            # Parse links and add to frontier
                            for link in res.normal_links:
                                if url_re.search(link):
                                    db.add_to_frontier(link)
                                    db.add_link(url, link)
                                else:
                                    print("Out of scope url: " + link)

                        else:
                            print("NON HTML", url, status_code, content_type)
                            # Save page as binary
                            db.page_content_binary(page_id=page_id, status=status_code, at=datetime.now())

                    else:
                        # TODO: what to do when hitting error page or non html page
                        pass


                except Exception as e:
                    # TODO: handle the errors of empty frontier or waiting for the site to be visited
                    print("Error caught: " + str(e))
                    self.lock.release()
                    return

            time.sleep(3)
