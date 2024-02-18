import time

import wx


brown = wx.Colour(165, 132, 82)


class MyFrame(wx.Frame):
    def __init__(self, parent=None):
        super(MyFrame, self).__init__(parent, title="Example for SDI", size=(500,500))
        # create status bar
        self.CreateStatusBar(1)
        self.SetStatusText("Developed by ophir")
        # create main panel - to put on the others panels
        self.panel = MainPanel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.panel, 1, wx.EXPAND)
        # arrange the frame
        self.SetSizer(box)
        self.Layout()
        self.Show()


class MainPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=(500, 500))
        self.frame = parent
        self.SetBackgroundColour(brown)
        self.login = LoginPanel(self, self.frame)
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        loginBtn = wx.Button(self, wx.ID_ANY, label="login", size=(100, 40))
        loginBtn.Bind(wx.EVT_BUTTON, self.go_to_log_in)
        btnBox.Add(loginBtn, 0, wx.ALL, 5)

        # add all elements to sizer
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Show()

    def go_to_log_in(self, event):
        self.Hide()
        self.login.Show()





class LoginPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=(500,500))
        self.frame = frame
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self,-1, label="Login Panel")
        titlefont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)
        nameBox = wx.BoxSizer(wx.HORIZONTAL)

        nameText = wx.StaticText(self, 1, label="UserName: ")

        self.nameField = wx.TextCtrl(self, -1, name="username", size=(150, -1))
        nameBox.Add(nameText, 0, wx.ALL, 5)
        nameBox.Add(self.nameField, 0, wx.ALL, 5)

        passBox = wx.BoxSizer(wx.HORIZONTAL)
        passText = wx.StaticText(self, 1, label="Password: ")

        self.passField = wx.TextCtrl(self, -1, name="password",style=wx.TE_PASSWORD,size=(150, -1))

        passBox.Add(passText, 0, wx.ALL, 5)
        passBox.Add(self.passField, 0,  wx.ALL, 5)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        loginBtn = wx.Button(self, wx.ID_ANY, label="login", size = (100, 40))
        loginBtn.Bind(wx.EVT_BUTTON, self.handle_login)
        btnBox.Add(loginBtn, 0, wx.ALL, 5)

        regBtn = wx.Button(self, wx.ID_ANY, label="Registration", size = ( 100, 40))
        regBtn.Bind(wx.EVT_BUTTON, self.handle_reg)
        btnBox.Add(regBtn, 1, wx.ALL, 5)

        # add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(10)
        sizer.Add(nameBox,0, wx.CENTER | wx.ALL, 5)
        sizer.Add(passBox,-1, wx.CENTER | wx.ALL, 5)
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
            self.frame.SetStatusText("Must enter name and password")
        else:
            self.frame.SetStatusText("waiting for Server approve")

    def handle_reg(self, event):
        self.frame.SetStatusText("hello")
        # self.parent.registration.Show()


if __name__ == '__main__':

    app = wx.App(False)
    first = MyFrame(None)
    app.MainLoop()
