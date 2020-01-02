import argparse, socket
import json
from config import DB_HOST, DB_NAME, DB_PASS, DB_USER, SERVER_HOST, SERVER_PORT


class DB:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def user_login(self, user_id, password):
        try:
            payload = {
                'login': {
                    'user_id': user_id,
                    'password': password
                }
            }
            payload = json.dumps(payload)
            sock.sendto(payload, (SERVER_HOST, SERVER_PORT))
            data, address = sock.recvfrom(1024)

            response = data.decode()

            if 'ok' in response and response['ok']:
                return response['userinfo']
            else:
                return False

        except Exception as e:
            print(e)
            return False
