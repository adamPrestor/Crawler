import concurrent.futures
import threading
import psycopg2

import settings

lock = threading.Lock()


def add_to_frontier(url, html, status):
    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password, dbname="postgres")
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("SELECT * FROM crawldb.page_type WHERE code='FRONTIER'")
    front = cur.fetchone()
    print(front[0])

    cur.execute("INSERT INTO crawldb.page (page_type_code, url, html_content, http_status_code)"
                " VALUES (%s,%s, %s, %s)", ('FRONTIER', url, html, status))

    cur.close()
    conn.close()


def get_frontier():
    conn = psycopg2.connect(host=settings.db_host, user=settings.db_username, password=settings.db_password)

    cur = conn.cursor()
    cur.execute("SELECT id FROM crawldb.page WHERE page_type_code IN "
                "(SELECT id FROM crawldb.page_type WHERE code='FRONTIER')")

    front = cur.fetchone()
    print(front)

    cur.close()
    conn.close()
