import re
import time

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
                print('I am here, doing nothing: ' + str(self.id))
                try:
                    # get the frontier out of the DB - FIFO style
                    self.lock.acquire()
                    page_id, url = db.get_frontier()
                    self.lock.release()

                    ran_out = False

                    print(str(self.id) + ',' + url)
                    # TODO: check the domain - urlparse etc.
                    # TODO: check for the delay on the domain - db.get_domain_last_visit

                    res = parser.parse_url(url)

                    # change the content of the page
                    # TODO: check the status of the returned url request
                    # TODO: add status to write into the database
                    # TODO: also the type of the page - in db function
                    db.page_content(html=getattr(res, 'html_content'), page_type=getattr(res, 'type'),
                                    url=url, status=200, at=getattr(res, 'access_time'))

                    # add all the binary content type to link to the page
                    for binary in getattr(res, 'binary_links'):
                        dtype = binary.split('.')[-1].upper()
                        print(dtype)
                        db.add_page_data(page=page_id, data=binary, data_type=dtype)

                    # add image data from the page
                    for image in getattr(res, 'image_links'):
                        # TODO
                        pass

                    # go through links
                    for link in getattr(res, 'normal_links'):
                        if url_re.search(link):
                            db.add_to_frontier(link)
                            db.add_link(url, link)
                        else:
                            print("Out of scope url: " + link)

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
