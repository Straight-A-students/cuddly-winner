import argparse
import socket
import json
from config import SERVER_HOST, SERVER_PORT
import traceback
import logging


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
            data = self.sock.recv(1024)
            self.sock.settimeout(None)
            logging.info('<--- server: %s', data.decode())
            data = json.loads(data.decode())
            return data
        except socket.timeout:
            self.sock.settimeout(None)
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

    def update_pos(self, pos):
        try:
            payload = {
                'move': {
                    'pos': pos
                }
            }
            self.send_message(payload)

        except Exception as e:
            traceback.print_exc()
            return (False, e)

    def turn_done(self, t_type, context):
        try:
            payload = {
                'turn_done':{
                    'type': t_type,
                    'context': context
                }
            }
            self.send_message(payload)

        except Exception as e:
            traceback.print_exc()
            return (False, e)

    def action_done(self, game_over, winner_name):
        try:
            payload = {
                'action_done': '',
                'game_over': game_over,
                'winner_name': winner_name
            }
            self.send_message(payload)

        except Exception as e:
            traceback.print_exc()
            return (False, e)