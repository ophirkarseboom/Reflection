import wx

def show_error(error: str):
    """
    gets error and tells it to user
    :param error: the error explanation
    """
    wx.MessageBox(error, "Error", wx.OK | wx.ICON_ERROR)

def show_notification(notification: str):
    """
    gets notification and tells it to user
    :param notification: the error explanation
    """
    wx.MessageBox(notification, "Notification", wx.OK | wx.ICON_ASTERISK)

