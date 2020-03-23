import concurrent.futures
import threading
import psycopg2
import psycopg2.errors
from datetime import datetime

from URL_parser import get_domain_name, get_robots_parser, fetch_robots

import settings

lock = threading.Lock()


def autoescape_html(html):
    return str(html).replace("\"", "\\\"").replace("\'", "\\\'")


def autoescape_html_udo(html):
    return str(html).replace("\\\"", "\"").replace("\\\'", "\'")


def add_to_frontier(url):
    """
    Push function. Will not add url to frontier, if it already exists in the base.
    :param url: URL to the page of interest.
    :return:
    """

    domain_name = get_domain_name(url)
    domain = get_domain(domain_name)
    if domain is None:
        robots_data = fetch_robots(url)
        add_domain(domain_name, robots_data, '')
        domain = get_domain(domain_name)

    print('DOMAIN', domain)

    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname=settings.db_database)
    conn.autocommit = True

    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO crawldb.page (page_type_code, url)"
                    " VALUES (%s,%s)", ('FRONTIER', url))
    except psycopg2.errors.UniqueViolation:
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
    cur.execute("SELECT id, url FROM crawldb.page WHERE page_type_code='FRONTIER' ORDER BY id")

    # get out of the frontier
    front = cur.fetchone()
    if not front:
        # frontier is empty
        print("The frontier is empty")
        cur.close()
        conn.close()
        return None
    else:
        # pop the first element out of the frontier
        id = front[0]

        # delete the page from teh frontier
        cur.execute(f"UPDATE crawldb.page SET page_type_code='HTML' WHERE id={id}")

        conn.commit()

        cur.close()
        conn.close()

        return front


def page_content(page_id, html, status, page_type, at):
    """

    :param page_id:
    :param html:
    :param status:
    :param page_type:
    :return:
    """
    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname=settings.db_database)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute(rf"""UPDATE crawldb.page
                     SET page_type_code='{page_type}',html_content='{autoescape_html('unicode_escape')}',http_status_code={status},accessed_time='{at}'
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
    cur.execute(f"INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time) VALUES "
                f"({page},{filename},{content_type},{data},{datetime.now()})")

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
    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname=settings.db_database)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute(f"INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES ('{domain_name}','{robots}','{site_map}')")

    cur.close()
    conn.close()


def get_domain_last_visit(domain_id):
    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password,
                            dbname=settings.db_database)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute(f"""SELECT accessed_time
                    FROM crawldb.page
                    WHERE page_type_code='HTML' and accessed_time IS NOT NULL
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
