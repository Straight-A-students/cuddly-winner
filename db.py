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
            self.cursor.execute("SELECT `user_id`, `user_name`, `password` FROM player WHERE user_id=%s", (user_id))
            row = self.cursor.fetchone()
            if row is None:
                return 1, None
            if row[2] != password:
                return 2, None
            return 0, (row[0], row[1])
        except Exception as e:
            traceback.print_exc()
            return False

    def user_signup(self, user_id, password, username):
        try:
            self.cursor.execute("INSERT INTO `player` (`user_id`, `password`, `user_name`) VALUES (%s, %s, %s)", (user_id, password, username))
            self.con.commit()
            return True
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

    def query_records(self, user_id):
        data = {
            'record': [],  # time, win(1/0)
            'rank': [],  # user_name, win_cnt
        }
        try:
            self.cursor.execute("SELECT `time`, `win` FROM record WHERE `user_id` = %s ORDER BY time DESC LIMIT 5", (user_id))
            rows = self.cursor.fetchall()
            for row in rows:
                if row[1] == 0:
                    data['record'].append([row[0].strftime("%Y/%m/%d, %H:%M:%S"), 'LOSS'])
                elif row[1] == 1:
                    data['record'].append([row[0].strftime("%Y/%m/%d, %H:%M:%S"), 'WIN'])
                elif row[1] == 2:
                    data['record'].append([row[0].strftime("%Y/%m/%d, %H:%M:%S"), 'DRAW'])

            self.cursor.execute(
                "SELECT user_name, SUM(win) AS wincnt FROM record LEFT JOIN player ON record.user_id = player.user_id WHERE record.win = 1 GROUP BY record.user_Id ORDER BY wincnt DESC LIMIT 5")
            rows = self.cursor.fetchall()
            for row in rows:
                data['rank'].append([row[0], int(row[1])])

            return data
        except Exception as e:
            traceback.print_exc()
            return data
