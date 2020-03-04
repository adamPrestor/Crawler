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

    def _find_links_and_data(self):
        a_elements = self.driver.find_elements_by_tag_name('a')
        links = [el.get_attribute('href') for el in a_elements]

        # TODO: filter links with pdf, doc, etc.

        img_elements = self.driver.find_elements_by_tag_name('img')
        images = [el.get_attribute('src') for el in img_elements]

        return links, images

    def parse_url(self, url):
        self.driver.get(url)

        # Timeout needed for Web page to render (read more about it)
        time.sleep(self.page_render_time)

        # Find links and images
        links, images = self._find_links_and_data()

        return self.driver.page_source

        # TODO: return links, content

    def close(self):
        self.driver.close()

    # Methods to enable use as context manager
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()