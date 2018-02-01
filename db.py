import psycopg2
from urllib import parse
import os

class DB:
    def __init__(self):
        parse.uses_netloc.append("postgres")
        url = parse.urlparse(os.environ["DATABASE_URL"])

        self.conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS urls (id SERIAL PRIMARY KEY, url VARCHAR NOT NULL);")

    def addURL(self, url):
        self.cur.execute("INSERT INTO urls (url) VALUES (%s)", [url])
        self.conn.commit()

    def checkURL(self, url):
        self.cur.execute("SELECT id FROM urls WHERE url = %s", [url])
        return self.cur.rowcount

    def clear(self):
        self.cur.execute('TRUNCATE TABLE urls')
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()
