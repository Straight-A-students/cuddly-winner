from db import DB
import socket
from config import SERVER_LISTEN, SERVER_PORT
import json

database = DB()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_LISTEN, SERVER_PORT))
print('Listening at {}'.format(sock.getsockname()))
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
            response['ok'] = True
            response['userinfo'] = userinfo
        except Exception:
            response['ok'] = False

    response = json.dumps(response)

    data = response.encode()
    sock.sendto(data, address)
