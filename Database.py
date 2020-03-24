import concurrent.futures
import threading
import psycopg2
import psycopg2.errors
from datetime import datetime, timedelta
import hashlib

from URL_parser import get_domain_name, get_robots_parser, fetch_robots, USER_AGENT, DEFAULT_CRAWL_DELAY

import settings

lock = threading.Lock()


class EmptyFrontierException(Exception):
    pass


class FrontierNotAvailableException(Exception):
    pass


def init_frontier():
    """ Init frontier on start. Add non-processed pages back to frontier. """

    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname=settings.db_database)
    conn.autocommit = True

    cur = conn.cursor()

    query = ("UPDATE crawldb.page "
             "SET page_type_code='FRONTIER' "
             "WHERE page_type_code IS NULL")
    cur.execute(query)

    cur.close()
    conn.close()

def add_to_frontier(url):
    """
    Push function. Will not add url to frontier, if it already exists in the base.
    :param url: URL to the page of interest.
    :return:
    """

    # Get domain data. If not existing, add a new domain.
    domain_name = get_domain_name(url)
    domain = get_domain(domain_name)

    # Get robots content from database or from url
    if domain is None:
        robots_data = fetch_robots(url)
        add_domain(domain_name, robots_data, '')
        domain = get_domain(domain_name)

    site_id = domain[0]
    robots_data = domain[2]

    # Parse robots.txt
    robots_parser = get_robots_parser(robots_data)
    delay = robots_parser.crawl_delay(USER_AGENT)

    if delay is not None:
        print('DELAY:', delay)

    # Check if URL can be crawled
    if not robots_parser.can_fetch(USER_AGENT, url):
        print("FORBIDDEN:", url)
        return


    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname=settings.db_database)
    conn.autocommit = True

    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO crawldb.page (site_id, page_type_code, url)"
                    f"VALUES ({site_id},'FRONTIER','{url}')")
    except psycopg2.errors.UniqueViolation:
        # TODO: fail silently
        print(f"Site '{url}' is already in the database.")

    cur.close()
    conn.close()


def get_frontier():
    """
    Pop function to get the front of the frontier.
    :return: The top element of the frontier
    """
    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname=settings.db_database)

    cur = conn.cursor()
    query = ("SELECT page.id, page.url FROM crawldb.page "
             "INNER JOIN crawldb.site ON page.site_id=site.id "
             "WHERE page.page_type_code='FRONTIER' "
             f"AND site.next_allowed_time <= '{datetime.now()}' "
             "ORDER BY page.id")
    cur.execute(query)

    # get out of the frontier
    front = cur.fetchone()
    if not front:
        # frontier is empty
        print("The frontier is empty")
        cur.close()
        conn.close()
        raise EmptyFrontierException
    else:
        # pop the first element out of the frontier
        id = front[0]

        # delete the page from teh frontier
        cur.execute(f"UPDATE crawldb.page SET page_type_code=NULL WHERE id={id}")

        conn.commit()

        cur.close()
        conn.close()

        # Update domain (set next access time)
        update_domain(id, datetime.now())

        return front

def _page_exists(md5_string, conn):
    """ Check if a page with given HTML already exists in the dataset. """

    cur = conn.cursor()

    cur.execute(rf"""SELECT url FROM crawldb.page WHERE html_content_hash='{md5_string}'""")
    front = cur.fetchone()

    cur.close()

    exists = front is not None
    url = front
    return exists, url

def page_content_binary(page_id, status, at):
    """ Updates page content (for binary files) """

    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname=settings.db_database)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute(rf"""UPDATE crawldb.page
                    SET page_type_code='BINARY',http_status_code={status},accessed_time='{at}'
                    WHERE id='{page_id}'""")

    cur.close()
    conn.close()


def page_content(page_id, url, html, status, page_type, at):
    """ Updates page content

    :param page_id:
    :param html:
    :param status:
    :param page_type:
    :return:
    """

    # TODO: locality hash instead
    # Compute hash
    md5_string = hashlib.md5(html.encode('utf-8')).hexdigest()

    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname=settings.db_database)
    conn.autocommit = True

    exists, duplicate_url = _page_exists(md5_string, conn)

    cur = conn.cursor()
    if not exists:
        # Not a duplicate
        sql = """UPDATE crawldb.page
                 SET page_type_code=%s,html_content=%s,html_content_hash=%s,http_status_code=%s,accessed_time=%s
                 WHERE id=%s"""
        cur.execute(sql, (page_type, html, md5_string, status, at, page_id))
    else:
        # Mark as duplicate
        print("DUPLICATE:", url, duplicate_url)
        cur.execute(rf"""UPDATE crawldb.page
                        SET page_type_code='DUPLICATE',http_status_code={status},accessed_time='{at}'
                        WHERE id='{page_id}'""")

    cur.close()
    conn.close()


def add_page_data(page, data, data_type):
    """

    :param page:
    :param data:
    :param data_type:
    :return:
    """
    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password,
                            dbname=settings.db_database)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute(f"INSERT INTO crawldb.page_data (page_id, data_type_code, data) VALUES ({page},'{data_type}','{data}')")

    cur.close()
    conn.close()


def add_image(page, filename, content_type, data):
    """

    :param page:
    :param filename:
    :param content_type:
    :param data:
    :return:
    """
    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password,
                            dbname=settings.db_database)
    conn.autocommit = True

    cur = conn.cursor()
    query = ("INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time) "
             f"VALUES ({page},{filename},{content_type},{data},{datetime.now()})")
    cur.execute()

    cur.close()
    conn.close()

def update_domain(page_id, access_time):
    """ Updates domain's next allowed time. """

    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname=settings.db_database)
    conn.autocommit = True

    cur = conn.cursor()
    query = ("SELECT site.id, site.crawl_delay FROM crawldb.page "
             "INNER JOIN crawldb.site ON page.site_id=site.id "
             f"WHERE page.id={page_id}")
    cur.execute(query)
    site_id, crawl_delay = cur.fetchone()

    # Add delay to access time
    next_allowed_time = access_time + timedelta(seconds=crawl_delay)

    print("DELAY", site_id, access_time, next_allowed_time)
    query = ("UPDATE crawldb.site "
             f"SET next_allowed_time='{next_allowed_time}' "
             f"WHERE id={site_id}")

    cur.execute(query)
    cur.close()

    conn.close()

def get_domain(domain):
    """

    :param domain:
    :return:
    """
    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname=settings.db_database)

    cur = conn.cursor()
    cur.execute(f"SELECT id, domain, robots_content FROM crawldb.site WHERE domain='{domain}'")

    front = cur.fetchone()

    cur.close()
    conn.close()

    return front


def add_domain(domain_name, robots, site_map):
    """

    :param domain_name:
    :param robots:
    :param site_map:
    :return:
    """

    # Get crawl delay
    robots_parser = get_robots_parser(robots)
    crawl_delay = robots_parser.crawl_delay(USER_AGENT)
    if crawl_delay is None:
        crawl_delay = DEFAULT_CRAWL_DELAY

    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname=settings.db_database)
    conn.autocommit = True

    cur = conn.cursor()
    query = ("INSERT INTO crawldb.site (domain, robots_content, sitemap_content, crawl_delay, next_allowed_time) "
             f"VALUES ('{domain_name}','{robots}','{site_map}', {crawl_delay}, '{datetime.now()}')")
    cur.execute(query)

    cur.close()
    conn.close()


def get_domain_last_visit(domain_id):
    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password,
                            dbname=settings.db_database)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute(f"""SELECT accessed_time
                    FROM crawldb.page
                    WHERE site_id={domain_id} and accessed_time IS NOT NULL
                    ORDER BY accessed_time DESC
                    LIMIT 1""")
    front = cur.fetchone()

    cur.close()
    conn.close()
    return front


def add_link(url_from, url_to):
    """

    :param url_from:
    :param url_to:
    :return:
    """
    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname=settings.db_database)
    conn.autocommit = True

    cur = conn.cursor()
    try:
        cur.execute(f"WITH id1(id) as (SELECT id FROM crawldb.page WHERE url='{url_from}'),"
                    f"id2(id) as (SELECT id FROM crawldb.page WHERE url='{url_to}')"
                    f"INSERT INTO crawldb.link (from_page, to_page) VALUES ((SELECT id from id1), (SELECT id from id2))")
    except psycopg2.errors.UniqueViolation:
        print(f"Link already exists: {url_from} -> {url_to}")

    cur.close()
    conn.close()
