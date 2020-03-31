# Database credentials
DB_USERNAME = 'user'
DB_PASSWORD = 'SecretPassword'
DB_HOST = 'localhost'
DB_DATABASE = 'postgres'

DRIVER_LOCATION = 'driver/chromedriver'
USER_AGENT = 'fri-ieps-group-7'

DEFAULT_NUM_WORKERS = 8
INIT_FRONTIER = [
    "https://www.gov.si/",
    "https://evem.gov.si/",
    "https://e-uprava.gov.si/",
    "https://e-prostor.gov.si/",
]

# Only crawl pages that match this regex
VALID_URL_REGEX = r'\.gov.si?/'

# Crawl delay used if robots.txt doesn't provide a value
DEFAULT_CRAWL_DELAY = 5

# Wait time for the page to render
DEFAULT_PAGE_WAIT = 5
