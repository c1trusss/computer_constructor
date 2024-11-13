import sqlite3


class Database:

    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)

    def execute(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)

    def __del__(self):
        self.connection.close()
