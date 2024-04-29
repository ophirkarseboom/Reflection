import wx
import wx.adv
import wx.media

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(300, 200))
        panel = wx.Panel(self)
        anim = wx.adv.Animation(r'C:\Users\ophir\PycharmProjects\Reflection\Reflection\graphics\icons\anim.gif', type=wx.adv.ANIMATION_TYPE_GIF)
        ctrl = wx.adv.AnimationCtrl(panel, wx.ID_ANY, anim, pos=(0, 0))
        ctrl.Play()
        self.Show()

if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame(None, "GIF Player")
    app.MainLoop()
