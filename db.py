import pymysql
from config import DB_HOST, DB_NAME, DB_PASS, DB_USER


class DB:
    con = None
    cursor = None

    def __init__(self):
        self.con = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASS,
            database=DB_NAME,
        )

        self.cursor = self.con.cursor()

    def user_login(self, tup):
        try:
            self.cursor.execute("SELECT * FROM player WHERE user_id=%s AND password=%s", tup)
            row = self.cursor.fetchone()
            print(row)
            return row
        except Exception as e:
            print(e)
            return False

    def add_record(self, tup):
        print(tup)
        try:
            self.cursor.execute("INSERT INTO `record` (`user_id`, `score`) VALUES (%s, %s)", tup)
            self.con.commit()
            return True
        except Exception as e:
            print(e)
            return False
