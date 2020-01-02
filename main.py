from login import LoginWindow

userinfo = None

login_window = LoginWindow()
login_window.add_frame()

userinfo = login_window.get_userinfo()
print(userinfo)
