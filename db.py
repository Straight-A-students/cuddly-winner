import pymysql
import traceback
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

    def user_login(self, user_id, password):
        try:
            self.cursor.execute("SELECT `user_id`, `user_name` FROM player WHERE user_id=%s AND password=%s", (user_id, password))
            row = self.cursor.fetchone()
            return row
        except Exception as e:
            traceback.print_exc()
            return False

    def add_record(self, user_id, win):
        try:
            self.cursor.execute("INSERT INTO `record` (`user_id`, `win`) VALUES (%s, %s)", (user_id, win))
            self.con.commit()
            return True
        except Exception as e:
            traceback.print_exc()
            return False
