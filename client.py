import argparse
import socket
import json
from config import SERVER_HOST, SERVER_PORT
import traceback


class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(None)

    def send_message(self, message):
        message = json.dumps(message).encode()
        self.sock.sendto(message, (SERVER_HOST, SERVER_PORT))

    def wait_server_message(self):
        try:
            self.sock.settimeout(0.01)
            # print('try to recv')
            data = self.sock.recv(1024)
            self.sock.settimeout(None)
            data = json.loads(data.decode())
            print(data)
            return data
        except socket.timeout:
            self.sock.settimeout(None)
            # print('Time out')
            return None

    def user_login(self, user_id, password):
        try:
            payload = {
                'login': {
                    'user_id': user_id,
                    'password': password
                }
            }
            self.send_message(payload)
            data = self.sock.recv(1024)
            print(data.decode())

            response = json.loads(data.decode())

            if 'ok' in response:
                if response['ok']:
                    return (True, response['userinfo'])
                else:
                    return (False, response['error'])
            else:
                return (False, 'Server Error.')

        except Exception as e:
            traceback.print_exc()
            return (False, e)

    def ready_done(self):
        try:
            payload = {
                'ready': 'done'
            }
            self.send_message(payload)

        except Exception as e:
            traceback.print_exc()
            return (False, e)

