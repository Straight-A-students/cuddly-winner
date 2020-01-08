import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(os.path.join(__file__, '..'))))

import pygame
from game import Game
from client import Client

linker = Client()

_, userinfo = linker.user_login(sys.argv[1], sys.argv[2])

game = Game(userinfo, linker)
game.run()
