import psycopg2

from .config import DATABASE_URL


def _conn():
    return psycopg2.connect(DATABASE_URL)


def query(sql, params=None):
    with _conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def execute(sql, params=None):
    with _conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.rowcount
