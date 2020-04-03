import re
import ssl
import time

import psycopg2
import requests
from datetime import datetime
import traceback
import logging
from multiprocessing import Process

from .URL_parser import URLParser

from . import Database as db
from . import settings

url_re = re.compile(settings.VALID_URL_REGEX)

class URLWorker(Process):
    """ Worker class. Retrieves and parses url and adds data to the dataset. """

    def __init__(self, lock, id):
        super().__init__()
        self.lock = lock
        self.id = id

    def run(self):
        ran_out = False
        with URLParser() as parser:
            while True:
                # Reads urls from queue until it receives the sentinel value of None
                try:
                    # get the frontier out of the DB - FIFO style
                    self.lock.acquire()
                    page_id, url = db.get_frontier()
                    self.lock.release()

                    ran_out = False

                    logging.debug(f"[{self.id}] Processing page: {url}")
                    print(f"[{self.id}] Processing page: {url}")

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
                                if len(dtype) > 10:
                                    # if dtype is longer then 5 then we can assume it is not the extension
                                    dtype = ''
                                db.add_image(page=page_id, filename=image, content_type=dtype, data=None, at=res.access_time)

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
                        logging.critical(f"Worker {self.id} has finished it's task. ---------------")
                        return
                    ran_out = True
                except ssl.SSLError:
                    logging.warning(f"Couldn't establish SSL connection to link {url}")
                except psycopg2.errors.StringDataRightTruncation:
                    logging.warning(f"Url was too long to save into the database {url}")
                except Exception as e:
                    logging.warning("Error caught: " + str(e), exc_info=True)
