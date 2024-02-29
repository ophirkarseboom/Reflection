import time
import wx
brown = wx.Colour(165, 132, 82)
import os
from pubsub import pub
from Reflection import settings
from queue import Queue
from Reflection.graphics.tree_graphic import TreePanel
from Reflection.graphics import notification


class MyFrame(wx.Frame):

    def __init__(self, logic_q: Queue):
        super(MyFrame, self).__init__(None, title="", size=(500, 500))
        # create status bar
        self.CreateStatusBar(1)
        self.SetStatusText("Developed by ophir")
        # create main panel - to put on the others panels
        self.panel = MainPanel(self)
        self.login = LoginPanel(self)
        self.register = RegisterPanel(self)
        self.logic_q = logic_q
        # self.tree = TreePanel(self, self.logic_q)

        # self.panel.Show()

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.panel, 1, wx.EXPAND)
        box.Add(self.login, 1, wx.EXPAND)
        box.Add(self.register, 1, wx.EXPAND)
        # box.Add(self.tree, 1, wx.EXPAND)


        # arrange the frame
        self.SetSizer(box)
        self.Layout()
        self.Show()

        self.panel.Show()
        pub.subscribe(notification.show_error, "error")
        pub.subscribe(notification.show_notification, "notification")


    def change_panel(self, current, new_panel):
        """
        switches between panels
        :param current: current panel working on
        :param new_panel: panel to switch to
        :return: None
        """
        self.SetStatusText("")
        current.Hide()
        new_panel.Show()


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
        loginBtn.Bind(wx.EVT_BUTTON, self.handle_login)
        registerBtn.Bind(wx.EVT_BUTTON, self.handle_register)
        btnBox.Add(loginBtn, 0, wx.ALL, 5)
        btnBox.Add(registerBtn, 0, wx.ALL, 5)

        # add all elements to sizer
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def handle_login(self, evt):
        """
        handles when client presses logs in
        :param evt: event
        :return: None
        """
        self.frame.change_panel(self, self.frame.login)

    def handle_register(self, evt):
        """
        handles when client presses register
        :param evt: event
        :return: None
        """
        self.frame.change_panel(self, self.frame.register)


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
        backBtn.Bind(wx.EVT_BUTTON, self.handle_back)
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
        """
        sends to logic username and password to register
        :param event: event got
        :return: None
        """
        username = self.nameField.GetValue()
        password = self.passField.GetValue()
        if not username or not password:
            notification.show_error('must enter username and password')
        else:
            self.parent.logic_q.put(('register', f'{username},{password}'))

    def handle_back(self, evt):
        """
        gets client back to main panel
        :param evt: event got
        :return: None
        """
        self.parent.change_panel(self, self.parent.panel)


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
        backBtn.Bind(wx.EVT_BUTTON, self.handle_back)
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

        pub.subscribe(self.go_to_tree, "login")

    def handle_login(self, event):
        """
        sends to logic login with username and password
        :param event: event got
        :return: None
        """
        username = self.nameField.GetValue()
        password = self.passField.GetValue()
        if not username or not password:
            self.Parent.SetStatusText("Must enter name and password")
        else:
            self.Parent.SetStatusText("waiting for Server approve")
            self.parent.logic_q.put(('login', f'{username},{password}'))


    def handle_back(self, evt):
        """
        gets back to main panel
        :param evt: event got
        :return: None
        """
        self.parent.change_panel(self, self.parent.panel)

    def go_to_tree(self):
        """
        goes to tree panel
        :return: None
        """
        print('got to go_to_tree')

        self.parent.Hide()
        TreePanel(self, self.parent.logic_q)

if __name__ == '__main__':
    graphic_q = Queue()
    a = wx.App(False)
    f = MyFrame(graphic_q)
    f.Show()
    a.MainLoop()
