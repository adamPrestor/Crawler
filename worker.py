import re
import time
import requests
from datetime import datetime
import traceback
import logging

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
        ran_out = False
        while True:
            with URLParser() as parser:
                # Reads urls from queue until it receives the sentinel value of None
                try:
                    # get the frontier out of the DB - FIFO style
                    self.lock.acquire()
                    page_id, url = db.get_frontier()
                    self.lock.release()

                    ran_out = False

                    logging.debug(f"{str(self.id)} :-> {url}")

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
                                db.add_page_data(page=page_id, data=binary, data_type=dtype)

                            # add image data from the page
                            for image in res.image_links:
                                dtype = image.split('.')[-1].upper()
                                db.add_image(page=page_id, filename=image, content_type=dtype, data=None,at=res.access_time)

                            # Parse links and add to frontier
                            for link in res.normal_links:
                                if url_re.search(link):
                                    if db.add_to_frontier(link):
                                        db.add_link(url, link)
                                else:
                                    logging.debug("Out of scope url: " + link)

                        else:
                            logging.debug(f"NON HTML: {url}  {status_code} {content_type}")
                            # Save page as binary
                            db.page_content_binary(page_id=page_id, status=status_code, at=datetime.now())

                    else:
                        # TODO: what to do when hitting error page or non html page
                        pass

                except db.FrontierNotAvailableException:
                    self.lock.release()
                    time.sleep(2)
                except db.EmptyFrontierException:
                    self.lock.release()
                    time.sleep(10)
                    if ran_out:
                        return
                    ran_out = True
                except Exception as e:
                    print("Error caught: " + str(e))

                    traceback.print_exc()
                    return
        logging.critical(f"Worker {self.id} has finished it's task. ---------------")
