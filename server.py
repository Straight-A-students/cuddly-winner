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


def get_user_idx_by_userid(username):
    if logged_in_users[0]['userinfo'][0] == address:
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
            status, userinfo = database.user_login(data['login']['user_id'], data['login']['password'])
            if status == 0:
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
            elif status == 1:
                send_message(address, {'ok': False, 'error': 'no_userid'})
            elif status == 2:
                send_message(address, {'ok': False, 'error': 'wrong_password'})
        except Exception as e:
            traceback.print_exc()
            send_message(address, {'ok': False, 'error': str(e)})
    elif 'signup' in data:
        database.user_signup(data['user_id'], data['password'], data['username'])
    elif 'ready' in data:
        logged_in_users[get_user_idx(address)]['status'] = 'ready_done'  # 將目前玩家改為 ready_done

        # 如果兩個玩家都 ready_done，則開始遊戲
        all_ready_done = True
        for i in range(2):
            if logged_in_users[i]['status'] != 'ready_done':
                all_ready_done = False
        if all_ready_done:
            pos1 = (200, 400)
            angle1 = 45
            pos2 = (1000, 400)
            angle2 = 135
            send_message(
                logged_in_users[0]['address'],
                {
                    'status': 'start',
                    'me': {'pos': pos1, 'angle': angle1},
                    'enemy': {'pos': pos2}
                }
            )
            send_message(
                logged_in_users[1]['address'],
                {
                    'status': 'start',
                    'me': {'pos': pos2, 'angle': angle2},
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
    elif 'action_done' in data:
        if data['game_over']:
            if 'game_over' not in logged_in_users[0] and 'game_over' not in logged_in_users[1]:
                logged_in_users[0]['game_over'] = True
                logged_in_users[1]['game_over'] = True

                user_idx = get_user_idx(address)
                if data['hp'][0] <= 0 and data['hp'][1] <= 0:
                    winner_name = ''
                    database.add_record(logged_in_users[0]['userinfo'][0], 2)
                    database.add_record(logged_in_users[1]['userinfo'][0], 2)
                elif data['hp'][0] > 0:
                    winner_name = logged_in_users[user_idx]['userinfo'][1]
                    database.add_record(logged_in_users[user_idx]['userinfo'][0], 1)
                    database.add_record(logged_in_users[1 - user_idx]['userinfo'][0], 0)
                else:
                    winner_name = logged_in_users[1 - user_idx]['userinfo'][1]
                    database.add_record(logged_in_users[user_idx]['userinfo'][0], 0)
                    database.add_record(logged_in_users[1 - user_idx]['userinfo'][0], 1)

                send_message(
                    logged_in_users[0]['address'],
                    {
                        'status': 'game_over',
                        'winner_name': winner_name,
                    }
                )
                send_message(
                    logged_in_users[1]['address'],
                    {
                        'status': 'game_over',
                        'winner_name': winner_name,
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
    elif 'query' in data:
        user_idx = get_user_idx(address)
        records = database.query_records(logged_in_users[user_idx]['userinfo'][0])
        send_message(
            address,
            records
        )
