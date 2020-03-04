import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import settings

class URLParser():
    def __init__(self, page_render_time=5, headless=True):

        self.page_render_time = page_render_time

        chrome_options = Options()

        # Use headless version of the browser
        chrome_options.headless = headless

        # Adding a specific user agent
        chrome_options.add_argument("user-agent=fri-ieps-group-7")

        self.driver = webdriver.Chrome(settings.DRIVER_LOCATION, options=chrome_options)

    def parse_url(self, url):
        self.driver.get(url)

        # Timeout needed for Web page to render (read more about it)
        time.sleep(self.page_render_time)

        return self.driver.page_source

        # TODO: search document for links, parse content

        # TODO: return links, content

    def close(self):
        self.driver.close()

    # Methods to enable use as context manager
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()