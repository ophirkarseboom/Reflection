import wx


class LoginFrame(wx.Frame):
    def __init__(self, parent, title):
        super(LoginFrame, self).__init__(parent, title=title, size=(300, 200))

        panel = wx.Panel(self)

        # Define the title label
        title_font = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title_text = wx.StaticText(panel, label="Login")
        title_text.SetFont(title_font)
        title_text.SetForegroundColour(wx.Colour(255, 255, 255))  # Custom text color
        title_text.SetBackgroundColour(wx.Colour(30, 30, 30))  # Custom background color

        # Add a subtle shadow effect
        title_shadow = wx.StaticText(panel, label="Login")
        title_shadow.SetFont(title_font)
        title_shadow.SetForegroundColour(wx.Colour(100, 100, 100))  # Shadow color
        title_shadow.SetPosition((title_text.GetPosition()[0] + 2, title_text.GetPosition()[1] + 2))

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer()
        sizer.Add(title_shadow, 0, wx.CENTER | wx.BOTTOM, border=5)
        sizer.Add(title_text, 0, wx.CENTER | wx.BOTTOM, border=5)
        panel.SetSizer(sizer)

        self.Centre()
        self.Show()


if __name__ == '__main__':
    app = wx.App()
    LoginFrame(None, title='Login')
    app.MainLoop()
