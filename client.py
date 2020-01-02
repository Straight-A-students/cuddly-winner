import argparse, socket
import json
from config import SERVER_HOST, SERVER_PORT
import traceback


class Client:
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
            payload = json.dumps(payload).encode()
            self.sock.sendto(payload, (SERVER_HOST, SERVER_PORT))
            data, _ = self.sock.recvfrom(1024)

            response = json.loads(data.decode())

            if 'ok' in response and response['ok']:
                return response['userinfo']
            else:
                return False

        except Exception as e:
            traceback.print_exc()
            return False
