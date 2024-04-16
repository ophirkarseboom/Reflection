import wx
import threading
import time


class LoadingPopup(wx.Dialog):
    def __init__(self, parent, message):
        super(LoadingPopup, self).__init__(parent, title="Loading", size=(200, 150),
                                           style=wx.DEFAULT_DIALOG_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.panel = wx.Panel(self)
        self.message_label = wx.StaticText(self.panel, label=message, style=wx.ALIGN_CENTER)
        self.dots_label = wx.StaticText(self.panel, label="...", style=wx.ALIGN_CENTER)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.message_label, 0, wx.ALL | wx.EXPAND, 5)

        # Horizontal sizer for message and dots labels
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.message_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        hbox.Add(self.dots_label, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.panel.SetSizer(sizer)
        self.Center()

        # Change cursor to a wait cursor
        wait_cursor = wx.Cursor(wx.CURSOR_WAIT)
        self.SetCursor(wait_cursor)

        # Start the animation timer
        self.animation_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_dots, self.animation_timer)
        self.animation_timer.Start(500)  # Adjust timing here (milliseconds)

        # Set the timer for automatic cancellation
        self.cancel_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.cancel_loading, self.cancel_timer)
        self.cancel_timer.Start(3000)  # 3 seconds

        # Initial dot count
        self.dot_count = 3

    def update_dots(self, event):
        if self.dot_count < 3:
            self.dots_label.SetLabel("." * self.dot_count)
            self.dot_count += 1
        else:
            self.dots_label.SetLabel("...")
            self.dot_count = 0

    def cancel_loading(self, event):
        self.Close()


def create_loading_popup(parent, message):
    popup = LoadingPopup(parent, message)
    popup.ShowModal()
    return popup


def do_long_task():
    # Simulate a long task
    for i in range(10):
        print("Task running...")
        time.sleep(1)


app = wx.App()
frame = wx.Frame(None)

loading_popup = create_loading_popup(frame, "Loading Task")

app.MainLoop()
