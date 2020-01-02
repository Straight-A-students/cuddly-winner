from login import LoginWindow
from game import Game

userinfo = None

login_window = LoginWindow()
login_window.add_frame()

userinfo = login_window.get_userinfo()
if not userinfo:
    exit()
print(userinfo)

game = Game(userinfo)
game.run()
del game
