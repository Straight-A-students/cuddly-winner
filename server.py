import json
import socket
import traceback

from config import SERVER_LISTEN, SERVER_PORT
from db import DB


database = DB()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_LISTEN, SERVER_PORT))
print('Listening at {}'.format(sock.getsockname()))


def send_message(to, message):
    print(to, message)
    message = json.dumps(message).encode()
    sock.sendto(message, to)


logged_in_users = []  # 紀錄已登入使用者
while True:
    data, address = sock.recvfrom(1024)
    text = data.decode()
    try:
        data = json.loads(text)
    except Exception:
        continue

    if 'login' in data:
        try:
            userinfo = database.user_login(data['login']['user_id'], data['login']['password'])
            if userinfo:
                if len(logged_in_users) >= 2:
                    send_message(address, {'ok': False, 'error': '房間已滿'})
                elif len(logged_in_users) == 1 and logged_in_users[0]['userinfo'][0] == userinfo[0]:
                    send_message(address, {'ok': False, 'error': '此帳號已在其他地方登入'})
                else:
                    send_message(address, {'ok': True, 'userinfo': userinfo})
                    logged_in_users.append({
                        'address': address,
                        'userinfo': userinfo
                    })
                    if len(logged_in_users) == 2:
                        send_message(logged_in_users[0]['address'], {'status': 'ready'})
                        send_message(logged_in_users[1]['address'], {'status': 'ready'})
            else:
                send_message(address, {'ok': False, 'error': '帳號或密碼錯誤'})
        except Exception as e:
            traceback.print_exc()
            send_message(address, {'ok': False, 'error': str(e)})
