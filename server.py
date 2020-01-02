import json
import socket

from config import SERVER_LISTEN, SERVER_PORT
from db import DB


database = DB()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_LISTEN, SERVER_PORT))
print('Listening at {}'.format(sock.getsockname()))
logged_in_users = []  # 紀錄已登入使用者
while True:
    data, address = sock.recvfrom(1024)
    text = data.decode()
    try:
        data = json.loads(text)
    except Exception:
        continue

    response = {}

    if 'login' in data:
        try:
            userinfo = database.user_login(data['login']['user_id'], data['login']['password'])
            if userinfo:
                if len(logged_in_users) == 0 or (len(logged_in_users) == 1 and logged_in_users[0][0] == userinfo[0]):
                    logged_in_users.append(userinfo)
                    response['ok'] = True
                    response['userinfo'] = userinfo
                else:
                    response['ok'] = False
            else:
                response['ok'] = False
        except Exception:
            response['ok'] = False

    response = json.dumps(response)

    data = response.encode()
    sock.sendto(data, address)
