import wx


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Tree Example", size=(400, 300))

        self.panel = wx.Panel(self)
        self.tree = wx.TreeCtrl(self.panel, style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT)

        self.root = self.tree.AddRoot("")
        gr = self.tree.AppendItem(self.root, "Grooveshark", data='nice')
        pop_r = self.tree.AppendItem(gr, "Popular")
        sr = self.tree.AppendItem(gr, "Search")

        dr = self.tree.AppendItem(self.root, "Download")

        pr = self.tree.AppendItem(self.root, "Pandora")
        stat_r = self.tree.AppendItem(pr, "Stations")



        image_list = wx.ImageList(16, 16)
        image_list.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16)))
        image_list.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))

        self.tree.AssignImageList(image_list)

        self.tree.SetItemImage(gr, 0, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(pop_r, 1, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(sr, 1, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(dr, 0, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(pr, 0, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(stat_r, 1, wx.TreeItemIcon_Normal)

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivated, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed, self.tree)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 1, wx.EXPAND)
        self.panel.SetSizer(sizer)

    def OnActivated(self, evt):
        print("Activated:", self.tree.GetItemText(evt.GetItem()))

    def OnItemExpanded(self, evt):
        print("Expanded:", self.tree.GetItemText(evt.GetItem()))

    def OnItemCollapsed(self, evt):
        print("Collapsed:", self.tree.GetItemText(evt.GetItem()))


if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
