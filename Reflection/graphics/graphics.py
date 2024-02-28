import time
import wx
brown = wx.Colour(165, 132, 82)
import os
from pubsub import pub
from Reflection import settings
from queue import Queue
from Reflection.graphics.tree_graphic import TreeFrame

class MyFrame(wx.Frame):
    def __init__(self, logic_q: Queue):
        super(MyFrame, self).__init__(None, title="Example for SDI", size=(500, 500))
        # create status bar
        self.CreateStatusBar(1)
        self.SetStatusText("Developed by ophir")
        # create main panel - to put on the others panels
        self.panel = MainPanel(self)
        self.login = LoginPanel(self)
        self.register = RegisterPanel(self)
        self.panel.Show()
        self.login.Hide()
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.panel, 1, wx.EXPAND)
        box.Add(self.login, 1, wx.EXPAND)

        self.logic_q = logic_q

        # arrange the frame
        self.SetSizer(box)
        self.Layout()
        self.Show()

        pub.subscribe(TreeFrame.show_error, "error")
        pub.subscribe(self.go_to_tree, "login")

    def go_to_login(self, event):
        self.panel.Hide()
        self.login.Show()

    def go_to_register(self, event):
        self.panel.Hide()
        self.register.Show()

    def go_back(self, event):
        if self.login.Shown:
            self.login.Hide()
        else:
            self.register.Hide()
        self.panel.Show()

    def go_to_tree(self):
        self.Hide()
        frame = TreeFrame(self.logic_q)
        frame.Show()
        self.Layout()



class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=(500, 500))
        self.frame = parent
        self.SetBackgroundColour(brown)
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)

        btnBox = wx.BoxSizer(wx.VERTICAL)
        loginBtn = wx.Button(self, wx.ID_ANY, label="Login", size=(200, 80))
        registerBtn = wx.Button(self, wx.ID_ANY, label="Register", size=(200, 80))
        loginBtn.Bind(wx.EVT_BUTTON, self.frame.go_to_login)
        registerBtn.Bind(wx.EVT_BUTTON, self.frame.go_to_register)
        btnBox.Add(loginBtn, 0, wx.ALL, 5)
        btnBox.Add(registerBtn, 0, wx.ALL, 5)

        # add all elements to sizer
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Show()

class RegisterPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=(500, 500))
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, -1, label="Registration")
        titlefont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)
        nameBox = wx.BoxSizer(wx.HORIZONTAL)

        nameText = wx.StaticText(self, 1, label="Username: ")

        self.nameField = wx.TextCtrl(self, -1, name="username", size=(150, -1))
        nameBox.Add(nameText, 0, wx.ALL, 5)
        nameBox.Add(self.nameField, 0, wx.ALL, 5)

        passBox = wx.BoxSizer(wx.HORIZONTAL)
        passText = wx.StaticText(self, 1, label="Password: ")

        self.passField = wx.TextCtrl(self, -1, name="password", style=wx.TE_PASSWORD, size=(150, -1))

        passBox.Add(passText, 0, wx.ALL, 5)
        passBox.Add(self.passField, 0, wx.ALL, 5)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)

        backBtn = wx.Button(self, wx.ID_ANY, label="back", size=(100, 40))
        backBtn.Bind(wx.EVT_BUTTON, self.parent.go_back)
        btnBox.Add(backBtn, 1, wx.ALL, 5)

        regBtn = wx.Button(self, wx.ID_ANY, label="Register", size=(100, 40))
        regBtn.Bind(wx.EVT_BUTTON, self.handle_reg)
        btnBox.Add(regBtn, 1, wx.ALL, 5)

        # add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(10)
        sizer.Add(nameBox, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(passBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(10)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)
        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def handle_reg(self, event):
        self.parent.SetStatusText("hello")
        # self.parent.registration.Show()


class LoginPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=(500, 500))
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, -1, label="Login")
        titlefont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)
        nameBox = wx.BoxSizer(wx.HORIZONTAL)

        nameText = wx.StaticText(self, 1, label="Username: ")

        self.nameField = wx.TextCtrl(self, -1, name="username", size=(150, -1))
        nameBox.Add(nameText, 0, wx.ALL, 5)
        nameBox.Add(self.nameField, 0, wx.ALL, 5)

        passBox = wx.BoxSizer(wx.HORIZONTAL)
        passText = wx.StaticText(self, 1, label="Password: ")

        self.passField = wx.TextCtrl(self, -1, name="password", style=wx.TE_PASSWORD, size=(150, -1))

        passBox.Add(passText, 0, wx.ALL, 5)
        passBox.Add(self.passField, 0, wx.ALL, 5)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        loginBtn = wx.Button(self, wx.ID_ANY, label="login", size=(100, 40))
        loginBtn.Bind(wx.EVT_BUTTON, self.handle_login)

        backBtn = wx.Button(self, wx.ID_ANY, label="back", size=(100, 40))
        backBtn.Bind(wx.EVT_BUTTON, self.parent.go_back)
        btnBox.Add(backBtn, 1, wx.ALL, 5)
        btnBox.Add(loginBtn, 0, wx.ALL, 5)

        # add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(10)
        sizer.Add(nameBox, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(passBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(10)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)
        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def handle_login(self, event):
        username = self.nameField.GetValue()
        password = self.passField.GetValue()
        if not username or not password:
            self.Parent.SetStatusText("Must enter name and password")
        else:
            self.Parent.SetStatusText("waiting for Server approve")
            self.parent.logic_q.put(('login', f'{username},{password}'))




if __name__ == '__main__':
    graphic_q = Queue()
    a = wx.App(False)
    f = MyFrame(graphic_q)
    f.Show()
    a.MainLoop()
