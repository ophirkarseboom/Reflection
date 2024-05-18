import time
import wx

import os
from pubsub import pub
from Reflection import settings
from queue import Queue
from Reflection.graphics.tree_graphic import TreeFrame
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

        self.SetIcon(wx.Icon(settings.Settings.icon_path))
        # self.panel.Show()

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.panel, 1, wx.EXPAND)
        box.Add(self.login, 1, wx.EXPAND)
        box.Add(self.register, 1, wx.EXPAND)


        # arrange the frame
        self.SetSizer(box)
        self.Layout()
        self.Show()

        self.panel.Show()
        pub.subscribe(TreeFrame.show_error, "error")


    def change_panel(self, current: wx.Panel, new_panel: wx.Panel):
        """
        switches between panels
        :param current: current panel working on
        :param new_panel: panel to switch to
        :return: None
        """
        current.Hide()
        new_panel.SetSize(current.GetSize())
        new_panel.Show()


    def go_to_tree(self):
        """
        goes to tree panel
        :return: None
        """
        self.Hide()
        TreeFrame(self, self.logic_q)


class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=(500, 500))
        self.frame = parent
        self.SetBackgroundColour(wx.Colour(30, 30, 30))
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)

        main_box = wx.BoxSizer(wx.VERTICAL)
        logo_image = wx.Image(os.path.join(settings.Settings.pic_path, "white_logo.png"))
        logo_image.Rescale(200, 50)
        logo_bitmap = wx.Bitmap(logo_image)
        logo = wx.StaticBitmap(self, bitmap=logo_bitmap)

        button_box = wx.BoxSizer(wx.HORIZONTAL)
        main_box.AddSpacer(15)
        main_box.Add(logo, 0, wx.CENTER | wx.ALL, 5)
        main_box.AddSpacer(20)
        loginBtn = wx.Button(self, wx.ID_ANY, label="Login", size=(200, 80))
        registerBtn = wx.Button(self, wx.ID_ANY, label="Register", size=(200, 80))
        loginBtn.Bind(wx.EVT_BUTTON, self.handle_login)
        registerBtn.Bind(wx.EVT_BUTTON, self.handle_register)
        button_box.Add(loginBtn, 0, wx.ALL, 5)
        button_box.Add(registerBtn, 0, wx.ALL, 5)
        main_box.Add(button_box, wx.CENTER | wx.TOP, 5)

        # add all elements to sizer
        sizer.Add(main_box, wx.CENTER | wx.ALL, 5)

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
        self.username = None
        self.password = None
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)
        bg_colour = wx.Colour(30, 30, 30)
        # Define the title label
        title_font = wx.Font(24, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        title_text = wx.StaticText(self, label="Register")
        title_text.SetFont(title_font)
        title_text.SetForegroundColour(wx.Colour(255, 255, 255))  # Custom text color

        nameBox = wx.BoxSizer(wx.HORIZONTAL)
        self.SetBackgroundColour(wx.Colour(bg_colour))
        self.SetForegroundColour(wx.Colour(150, 150, 150))
        nameText = wx.StaticText(self, 1, label="Username: ")

        self.nameField = wx.TextCtrl(self, -1, name="username", size=(150, -1))
        self.nameField.SetBackgroundColour(wx.Colour(50, 50, 50))  # Custom background color
        self.nameField.SetForegroundColour(wx.Colour(255, 255, 255))
        nameBox.Add(nameText, 0, wx.ALL, 5)
        nameBox.Add(self.nameField, 0, wx.ALL, 5)

        passBox = wx.BoxSizer(wx.HORIZONTAL)
        passText = wx.StaticText(self, 1, label="Password: ")
        # passText.SetFont()

        self.passField = wx.TextCtrl(self, -1, name="password", style=wx.TE_PASSWORD, size=(150, -1))
        self.passField.SetBackgroundColour(wx.Colour(50, 50, 50))  # Custom background color
        self.passField.SetForegroundColour(wx.Colour(255, 255, 255))

        passBox.Add(passText, 0, wx.ALL, 5)
        passBox.Add(self.passField, 0, wx.ALL, 5)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)

        login_button = wx.Button(self, label="Register")
        login_button.SetBackgroundColour(wx.Colour(50, 50, 50))  # Custom background color
        login_button.SetForegroundColour(wx.Colour(255, 255, 255))  # Custom text color
        login_button.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        login_button.Bind(wx.EVT_BUTTON, self.handle_reg)

        back_btn = wx.Button(self, wx.ID_ANY, label="Back")
        back_btn.SetBackgroundColour(wx.Colour(50, 50, 50))  # Custom background color
        back_btn.SetForegroundColour(wx.Colour(255, 255, 255))  # Custom text color
        back_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        back_btn.Bind(wx.EVT_BUTTON, self.handle_back)
        btnBox.Add(back_btn, 1, wx.ALL, 5)
        btnBox.Add(login_button, 0, wx.ALL, 5)

        # add all elements to sizer
        sizer.AddStretchSpacer(20)
        sizer.Add(title_text, 0, wx.CENTER | wx.BOTTOM, border=0)

        sizer.AddSpacer(10)
        sizer.Add(nameBox, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(passBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(10)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)
        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

        pub.subscribe(self.parent.go_to_tree, "login")
        pub.subscribe(self.do_login, 'register_ok')

    def handle_reg(self, event):
        """
        sends to logic username and password to register
        :param event: event got
        :return: None
        """
        self.username = self.nameField.GetValue()
        self.password = self.passField.GetValue()
        if not self.username or not self.password:
            TreeFrame.show_error('must enter username and password')
        else:
            self.parent.logic_q.put(('register', f'{self.username},{self.password}'))

    def handle_back(self, evt):
        """
        gets client back to main panel
        :param evt: event got
        :return: None
        """
        self.parent.change_panel(self, self.parent.panel)

    def do_login(self):
        """
        calls login
        :return: none
        """
        if self.username and self.password:
            self.parent.logic_q.put(('login', f'{self.username},{self.password}'))

class LoginPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=(500, 500))
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)
        bg_colour = wx.Colour(30, 30, 30)
        # Define the title label
        title_font = wx.Font(24, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        title_text = wx.StaticText(self, label="Login")
        title_text.SetFont(title_font)
        title_text.SetForegroundColour(wx.Colour(255, 255, 255))  # Custom text color

        nameBox = wx.BoxSizer(wx.HORIZONTAL)
        self.SetBackgroundColour(wx.Colour(bg_colour))
        self.SetForegroundColour(wx.Colour(150, 150, 150))
        nameText = wx.StaticText(self, 1, label="Username: ")

        self.nameField = wx.TextCtrl(self, -1, name="username", size=(150, -1))
        self.nameField.SetBackgroundColour(wx.Colour(50, 50, 50))  # Custom background color
        self.nameField.SetForegroundColour(wx.Colour(255, 255, 255))
        nameBox.Add(nameText, 0, wx.ALL, 5)
        nameBox.Add(self.nameField, 0, wx.ALL, 5)

        passBox = wx.BoxSizer(wx.HORIZONTAL)
        passText = wx.StaticText(self, 1, label="Password: ")
        # passText.SetFont()

        self.passField = wx.TextCtrl(self, -1, name="password", style=wx.TE_PASSWORD, size=(150, -1))
        self.passField.SetBackgroundColour(wx.Colour(50, 50, 50))  # Custom background color
        self.passField.SetForegroundColour(wx.Colour(255, 255, 255))

        passBox.Add(passText, 0, wx.ALL, 5)
        passBox.Add(self.passField, 0, wx.ALL, 5)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)

        login_button = wx.Button(self, label="Login")
        login_button.SetBackgroundColour(wx.Colour(50, 50, 50))  # Custom background color
        login_button.SetForegroundColour(wx.Colour(255, 255, 255))  # Custom text color
        login_button.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        login_button.Bind(wx.EVT_BUTTON, self.handle_login)

        back_btn = wx.Button(self, wx.ID_ANY, label="Back")
        back_btn.SetBackgroundColour(wx.Colour(50, 50, 50))  # Custom background color
        back_btn.SetForegroundColour(wx.Colour(255, 255, 255))  # Custom text color
        back_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        back_btn.Bind(wx.EVT_BUTTON, self.handle_back)
        btnBox.Add(back_btn, 1, wx.ALL, 5)
        btnBox.Add(login_button, 0, wx.ALL, 5)

        # add all elements to sizer
        sizer.AddStretchSpacer(20)
        sizer.Add(title_text, 0, wx.CENTER | wx.BOTTOM, border=0)

        sizer.AddSpacer(10)
        sizer.Add(nameBox, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(passBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(10)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)
        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

        pub.subscribe(self.parent.go_to_tree, "login")

    def handle_login(self, event):
        """
        sends to logic login with username and password
        :param event: event got
        :return: None
        """
        username = self.nameField.GetValue()
        password = self.passField.GetValue()
        if not username or not password:
            TreeFrame.show_error('must enter name and password')
        else:
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
        self.parent.Hide()
        TreeFrame(self, self.parent.logic_q)

if __name__ == '__main__':
    graphic_q = Queue()
    a = wx.App(False)
    f = MyFrame(graphic_q)
    f.Show()
    a.MainLoop()
