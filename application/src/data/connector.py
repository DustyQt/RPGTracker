import sqlite3

class Connector:
    def __init__(self):
        self.conn = sqlite3.connect('database')

    def query(self, query):
        cur = self.conn.cursor()
        res = cur.execute(query)
        return res.fetchall()


