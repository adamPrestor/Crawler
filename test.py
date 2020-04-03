from multiprocessing import Queue
from worker import URLWorker
import queue

links = [
    'https://www.plus2net.com/html_tutorial/button-linking.php',
    'http://petrac.si/',
    "https://www.google.com",
    "https://www.gov.si/",
    "https://evem.gov.si/",
    "https://e-uprava.gov.si/",
    "https://e-prostor.gov.si/"
]

NUM_WORKERS = 5
frontier_queue = Queue()
response_queue = Queue()

for i in range(NUM_WORKERS):
    URLWorker(frontier_queue, response_queue).start()

# Add initial frontier urls
for url in links:
    frontier_queue.put(url)

# Processing loop (recieve urls, add to frontier)
while True:
    try:
        element = response_queue.get(timeout=10)
        print(element)
    except queue.Empty:
        break

# Send exit signal to workers
for i in range(NUM_WORKERS):
    frontier_queue.put(None)
