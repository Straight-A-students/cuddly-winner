from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog


class LoginWindow:
    userinfo = None

    def __init__(self, linker):
        self.linker = linker
        self.win = Tk()

        self.win.iconbitmap('images/icon_white.ico')

        # reset the window and background color
        self.canvas = Canvas(self.win,
                             width=600, height=500,
                             bg='white')
        self.canvas.pack(expand=YES, fill=BOTH)

        # show window in center of the screen
        width = self.win.winfo_screenwidth()
        height = self.win.winfo_screenheight()
        x = int(width / 2 - 600 / 2)
        y = int(height / 2 - 500 / 2)
        str1 = "600x500+" + str(x) + "+" + str(y)
        self.win.geometry(str1)

        # disable resize of the window
        self.win.resizable(width=False, height=False)

        # change the title of the window
        self.win.title("歡迎來到 Cuddly Winner | 登入畫面")

    def add_frame(self):
        self.frame = Frame(self.win, height=400, width=450)
        self.frame.place(x=80, y=50)

        x, y = 70, 20

        self.img = PhotoImage(file='images/icon.png')
        self.label = Label(self.frame, image=self.img)
        self.label.place(x=x + 105, y=y + 0)

        # now create a login form
        self.label = Label(self.frame, text="Player Login")
        self.label.config(font=("Courier", 20, 'bold'))
        self.label.place(x=140, y=y + 150)

        self.uidlabel = Label(self.frame, text="User ID:")
        self.uidlabel.config(font=("Courier", 12, 'bold'))
        self.uidlabel.place(x=50, y=y + 230)

        self.userid = Entry(self.frame, font='Courier 12')
        self.userid.place(x=170, y=y + 230)

        self.pwdlabel = Label(self.frame, text="Password:")
        self.pwdlabel.config(font=("Courier", 12, 'bold'))
        self.pwdlabel.place(x=50, y=y + 260)

        self.password = Entry(self.frame, show='*',
                              font='Courier 12')
        self.password.place(x=170, y=y + 260)

        self.button = Button(self.frame, text="Login",
                             font='Courier 15 bold',
                             command=self.login)
        self.button.place(x=170, y=y + 290)

        self.win.mainloop()

    def login(self):
        # get the data and store it into tuple (data)
        user_id = self.userid.get(),
        password = self.password.get()
        # validations
        if user_id == "":
            messagebox.showinfo("Alert!", "Enter UserID First")
        elif password == "":
            messagebox.showinfo("Alert!", "Enter Password First")
        else:
            state, userinfo = self.linker.user_login(user_id, password)
            if state:
                messagebox.showinfo("Message", "Login Successfully")
                self.win.destroy()
                self.userinfo = userinfo
            else:
                if userinfo == 'no_userid':
                    user_name = simpledialog.askstring(
                        '註冊帳號',
                        '君の名は？',
                        parent=self.win
                    )
                    if user_name:
                        self.linker.signup(user_id, password, user_name)
                        _, userinfo = self.linker.user_login(user_id, password)
                        messagebox.showinfo("Message", "Login Successfully")
                        self.win.destroy()
                        self.userinfo = userinfo
                    else:
                        messagebox.showinfo("ALert!", '請重新登入或輸入名字以註冊帳號')
                        userinfo = None
                elif userinfo == 'wrong_password':
                    messagebox.showinfo("ALert!", '密碼錯誤')
                    userinfo = None
                else:
                    messagebox.showinfo("ALert!", userinfo)
                    userinfo = None

    def get_userinfo(self):
        return self.userinfo
