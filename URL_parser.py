import re
import time
from datetime import datetime
from collections import namedtuple
import urllib
from protego import Protego

import requests
import urltools
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import settings

USER_AGENT = 'fri-ieps-group-7'
DEFAULT_CRAWL_DELAY = 5

ParserResult = namedtuple('ParserResult', ['html_content', 'access_time',
                                           'image_links', 'binary_links', 'normal_links'])

def is_image(url):
    """ Check if url is an image (from url string) """

    ext = ['.jpg', '.jpeg', '.bmp', '.png', '.svg', '.gif', '.tiff', '.tif']
    return any(url.lower().endswith(e) for e in ext)

def is_binary(url):
    """ Check if url is a binary page (from url string) """

    ext = ['.pdf', '.doc', '.docx', '.ppt', '.pptx']
    return any(url.lower().endswith(e) for e in ext)

def group_split(seq, *filter_fns):
    """ Splits arr into multiple groups based on filter functions. """

    filter_groups = [set() for fn in filter_fns]
    rest_group = set()
    for el in seq:
        # Add element to first matching group
        for fn, group in zip(filter_fns, filter_groups):
            if fn(el):
                group.add(el)
                break
        # If no matching groups, add it to the rest group
        else:
            rest_group.add(el)

    groups = tuple([*filter_groups, rest_group])
    return groups

def fetch_robots(url):
    """ Reads robots file (if present) for the domain of the given url. If the robots.txt file is missing an empty string is returned. """

    parsed = urllib.parse.urlparse(url)
    robots_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, 'robots.txt', '', '', ''))

    robots_data = ''
    try:
        res = requests.get(robots_url)
        if res.status_code == 200:
            robots_data = res.content.decode('utf-8')
    except requests.RequestException:
        print(f'WARNING: Could not read robots file: {robots_url}')

    return robots_data

def get_robots_parser(data):
    """ Gets robots parser from robots.txt data. """

    robots = Protego.parse(data)

    return robots

def get_domain_name(url):
    """ Return the domain of the page. """

    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc
    return domain

def canonicalize_url(url):
    # Canonicalize URL
    url = urltools.normalize(url)

    # Remove fragment
    url = urllib.parse.urldefrag(url).url

    return url

class URLParser():
    def __init__(self, page_render_time=5, headless=True):

        self.page_render_time = page_render_time

        chrome_options = Options()

        # Use headless version of the browser
        chrome_options.headless = headless

        # Adding a specific user agent
        chrome_options.add_argument(f"user-agent={USER_AGENT}")

        self.driver = webdriver.Chrome(settings.DRIVER_LOCATION, options=chrome_options)

        # Onclick regex
        self.onclick_regex = re.compile(r'location(?:\.href)*\s*=\s*["\']([^\s"\']*)["\']')

    def _find_links_and_data(self):
        # <a href=...> elements
        a_elements = self.driver.find_elements_by_tag_name('a[href]')
        links = {el.get_attribute('href') for el in a_elements}

        # Filter non links
        links = {l for l in links if l.startswith('http')}

        # <* onclick=...> elements
        onclick_elements = self.driver.find_elements_by_css_selector('*[onclick]')
        onclicks = [el.get_attribute('onclick') for el in onclick_elements]

        # Find links in onclick code
        onclick_links = set()
        for onclick in onclicks:
            search_obj = self.onclick_regex.search(onclick)
            if search_obj is not None:
                url = search_obj.groups()[0]
                onclick_links.add(url)

        all_links = links | onclick_links

        # Convert relative paths to absolute
        base_url = self.driver.current_url
        all_links = {urllib.parse.urljoin(base_url, url) for url in all_links}

        # Canonicalize all_links
        all_links = {canonicalize_url(link) for link in all_links}

        # Find images
        img_elements = self.driver.find_elements_by_tag_name('img[src]')
        images = {el.get_attribute('src') for el in img_elements}

        # Filter non links (images) and canonicalize
        images = {canonicalize_url(i) for i in images if i.startswith('http')}

        image_links, binary_links, other_links = group_split(all_links, is_image, is_binary)
        image_links = images | image_links

        return other_links, image_links, binary_links

    def parse_url(self, url):
        # TODO: send HEAD request with other library to get status code and page type

        self.driver.get(url)

        access_time = datetime.now()

        # Timeout needed for Web page to render (read more about it)
        time.sleep(self.page_render_time)

        # Content
        html_content = self.driver.page_source

        # Find links and images
        normal_links, images, binary_files = self._find_links_and_data()

        return ParserResult(html_content=html_content, access_time=access_time,
                            image_links=images, binary_links=binary_files, normal_links=normal_links)

    def close(self):
        self.driver.quit()

    # Methods to enable use as context manager
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
