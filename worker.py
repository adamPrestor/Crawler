from URL_parser import URLParser
from multiprocessing import Process

class URLWorker(Process):
    """ Worker class. Retrieves and parses url and adds data to the dataset. """

    def __init__(self, queue_in, queue_out):
        super().__init__()
        self.queue_in = queue_in
        self.queue_out = queue_out

    def run(self):
        with URLParser() as parser:
            # Reads urls from queue until it receives the sentinel value of None
            for url in iter(self.queue_in.get, None):
                print(url)
                res = parser.parse_url(url)

                # TODO: add results to dataset

                # Send normal links to manager
                self.queue_out.put(res.normal_links)

