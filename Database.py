import concurrent.futures
import threading
import psycopg2

import settings

lock = threading.Lock()


def add_to_frontier(url):
    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname=settings.db_password)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("INSERT INTO crawldb.page (page_type_code, url)"
                " VALUES (%s,%s, %s, %s)", ('FRONTIER', url))

    conn.commit()

    cur.close()
    conn.close()


def get_frontier():
    """
    Pop function
    :return: The top element of the frontier
    """
    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname=settings.db_database)

    cur = conn.cursor()
    cur.execute("SELECT id, url FROM crawldb.page WHERE page_type_code='FRONTIER'")

    # get out of the frontier
    front = cur.fetchone()
    id = front[0]

    print(id)

    # delete the page from teh frontier
    cur.execute("UPDATE crawldb.page SET page_type_code='HTML' WHERE id=1")

    conn.commit()

    cur.close()
    conn.close()

    return front


def get_domain(domain):
    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname=settings.db_database)

    cur = conn.cursor()
    cur.execute("SELECT * FROM crawldb.site WHERE domain=%s", domain)

    front = cur.fetchone()
    print(front)

    cur.close()
    conn.close()


def add_domain(domain, robots, site_map):
    raise NotImplementedError


def add_link(url_from, url_to):
    raise NotImplementedError


def add_content():
    raise NotImplementedError
