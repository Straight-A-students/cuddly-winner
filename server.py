import json
import socket
import traceback
import logging

from config import SERVER_LISTEN, SERVER_PORT
from db import DB

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

database = DB()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_LISTEN, SERVER_PORT))
logging.info('Listening at %s', sock.getsockname())


def send_message(to, message):
    logging.info('---> %s: %s', to, message)
    message = json.dumps(message).encode()
    sock.sendto(message, to)


def get_user_idx(address):
    if logged_in_users[0]['address'] == address:
        return 0
    return 1


logged_in_users = []  # 紀錄已登入使用者
while True:
    try:
        data, address = sock.recvfrom(1024)
    except Exception as e:
        print(e)
        continue
    text = data.decode()
    try:
        data = json.loads(text)
    except Exception:
        continue

    logging.info('<--- %s: %s', address, text)

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
                        'userinfo': userinfo,
                        'status': 'waiting',
                    })
                    if len(logged_in_users) == 2:
                        for i in range(2):
                            send_message(logged_in_users[i]['address'], {'status': 'ready'})
                            logged_in_users[i]['status'] = 'ready'
            else:
                send_message(address, {'ok': False, 'error': '帳號或密碼錯誤'})
        except Exception as e:
            traceback.print_exc()
            send_message(address, {'ok': False, 'error': str(e)})

    elif 'ready' in data:
        logged_in_users[get_user_idx(address)]['status'] = 'ready_done'  # 將目前玩家改為 ready_done

        # 如果兩個玩家都 ready_done，則開始遊戲
        all_ready_done = True
        for i in range(2):
            if logged_in_users[i]['status'] != 'ready_done':
                all_ready_done = False
        if all_ready_done:
            pos1 = (200, 350)
            pos2 = (1000, 350)
            send_message(
                logged_in_users[0]['address'],
                {
                    'status': 'start',
                    'me': {'pos': pos1},
                    'enemy': {'pos': pos2}
                }
            )
            send_message(
                logged_in_users[1]['address'],
                {
                    'status': 'start',
                    'me': {'pos': pos2},
                    'enemy': {'pos': pos1}
                }
            )
    elif 'move' in data:
        user_idx = get_user_idx(address)
        send_message(
            logged_in_users[1 - user_idx]['address'],
            {
                'status': 'update',
                'enemy': {
                    'pos': data['move']['pos']
                }
            }
        )
    elif 'turn_done' in data:
        user_idx = get_user_idx(address)
        logged_in_users[user_idx]['turn_done'] = {
            'type': data['turn_done']['type'],
            'context': data['turn_done']['context'],
        }
        if 'turn_done' in logged_in_users[0] and 'turn_done' in logged_in_users[1]:
            send_message(
                logged_in_users[0]['address'],
                {
                    'status': 'action',
                    'type': logged_in_users[1]['turn_done']['type'],
                    'context': logged_in_users[1]['turn_done']['context'],
                }
            )
            send_message(
                logged_in_users[1]['address'],
                {
                    'status': 'action',
                    'type': logged_in_users[0]['turn_done']['type'],
                    'context': logged_in_users[0]['turn_done']['context'],
                }
            )
            del logged_in_users[0]['turn_done']
            del logged_in_users[1]['turn_done']
    elif 'action_done':
        if data['game_over']:
            send_message(
                logged_in_users[0]['address'],
                {
                    'status': 'game_over',
                }
            )
            send_message(
                logged_in_users[1]['address'],
                {
                    'status': 'game_over',
                }
            )
        else:
            user_idx = get_user_idx(address)
            logged_in_users[user_idx]['action_done'] = True
            if 'action_done' in logged_in_users[0] and 'action_done' in logged_in_users[1]:
                send_message(
                    logged_in_users[0]['address'],
                    {
                        'status': 'action_done',
                    }
                )
                send_message(
                    logged_in_users[1]['address'],
                    {
                        'status': 'action_done',
                    }
                )
                del logged_in_users[0]['action_done']
                del logged_in_users[1]['action_done']
