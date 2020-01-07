import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(os.path.join(__file__, '..'))))

import pygame
from game import Game
from client import Client

linker = Client()

game = Game(['test', 'Test User'], linker)
game.status = game.STATUS_READY
game.run()
