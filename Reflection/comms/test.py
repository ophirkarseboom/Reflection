import wx

class TestFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1)

        self.tree = wx.TreeCtrl(self, style=wx.TR_HIDE_ROOT)
        self.root = self.tree.AddRoot("")

        dic = {'D:\\reflection\\yotam\\': ['192.168.4.96', ','], 'D:\\reflection\\yotam\\192.168.4.96': ['folder', 'folder1', 'folder10', 'folder2', 'folder3', 'folder4', 'folder5', 'folder6', 'folder7', ',', 'file.txt', 'hi.docx'], 'D:\\reflection\\yotam\\192.168.4.96\\folder': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder1': ['in1', ','], 'D:\\reflection\\yotam\\192.168.4.96\\folder1\\in1': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder10': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder2': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder3': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder4': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder5': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder6': ['folder_in_6', ',', 'a.txt'], 'D:\\reflection\\yotam\\192.168.4.96\\folder6\\folder_in_6': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder7': [',', 'a.txt', 'b.txt']}

        gr = self.tree.AppendItem(self.root, "Grooveshark")
        pop_r = self.tree.AppendItem(gr, "Popular")
        sr = self.tree.AppendItem(gr, "Search")

        dr = self.tree.AppendItem(self.root, "Download")

        pr = self.tree.AppendItem(self.root, "Pandora")
        stat_r = self.tree.AppendItem(pr, "Stations")

        image_list = wx.ImageList(16, 16)
        grooveshark = image_list.Add(wx.Image(r"T:\public\cyber\ophir\Reflection\Reflection\comms\image.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
        popular     = image_list.Add(wx.Image(r"T:\public\cyber\ophir\Reflection\Reflection\comms\image.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
        search      = image_list.Add(wx.Image(r"T:\public\cyber\ophir\Reflection\Reflection\comms\image.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
        download    = image_list.Add(wx.Image(r"T:\public\cyber\ophir\Reflection\Reflection\comms\image.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
        pandora     = image_list.Add(wx.Image(r"T:\public\cyber\ophir\Reflection\Reflection\comms\image.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
        stations    = image_list.Add(wx.Image(r"T:\public\cyber\ophir\Reflection\Reflection\comms\image.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())

        self.tree.AssignImageList(image_list)

        self.tree.SetItemData(gr, "aaa")
        self.tree.SetItemImage(gr, grooveshark, wx.TreeItemIcon_Normal)
        self.tree.SetItemData(pop_r, 2)
        self.tree.SetItemImage(pop_r, popular, wx.TreeItemIcon_Normal)
        self.tree.SetItemData(sr, 3)
        self.tree.SetItemImage(sr, search, wx.TreeItemIcon_Normal)
        self.tree.SetItemData(dr, 4)
        self.tree.SetItemImage(dr, download, wx.TreeItemIcon_Normal)
        self.tree.SetItemData(pr, 5)
        self.tree.SetItemImage(pr, pandora, wx.TreeItemIcon_Normal)
        self.tree.SetItemData(stat_r, 6)
        self.tree.SetItemImage(stat_r, stations, wx.TreeItemIcon_Normal)

        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnActivated, self.tree)
        #self.Bind(wx.TreeCt, self.OnActivated, self.tree)

    def OnActivated(self, evt):
        print("hello")
        print('Double clicked on', self.tree.GetItemData(evt.GetItem()))



if __name__ == "__main__":
    a = wx.App(False)

    f = TestFrame()
    f.Show()
    a.MainLoop()