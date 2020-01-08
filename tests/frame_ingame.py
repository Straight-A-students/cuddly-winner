import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(os.path.join(__file__, '..'))))

import pygame
import logging
from game import Game
from client import Client

linker = Client()

_, userinfo = linker.user_login(sys.argv[1], sys.argv[2])
logging.info('Login in as : %s', userinfo)

game = Game(userinfo, linker)
game.run()
