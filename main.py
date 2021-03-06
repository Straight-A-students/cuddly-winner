from login import LoginWindow
from game import Game
from client import Client
import logging

linker = Client()

userinfo = None

login_window = LoginWindow(linker)
login_window.add_frame()

userinfo = login_window.get_userinfo()
if not userinfo:
    exit()
logging.info('Login in as : %s', userinfo)

game = Game(userinfo, linker)
game.run()
del game
