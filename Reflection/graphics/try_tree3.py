import glob
import os
import wx

########################################################################
class MyTreeCtrl(wx.TreeCtrl):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.TreeCtrl.__init__(self, parent,wx.TR_HAS_BUTTONS)


########################################################################
class MyPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)


        self.tree = MyTreeCtrl(self)

        # isz = (16,16)
        # il = wx.ImageList(isz[0], isz[1])
        # self.fldridx = il.Add(wx.Image(r"D:\year24\merry\trytrees\folder.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
        # self.fldropenidx = il.Add(wx.Image(r"D:\year24\merry\trytrees\openfolder.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
        # self.fileidx = il.Add(wx.Image(r"D:\year24\merry\trytrees\file.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
        # self.tree.SetImageList(il)

        self.root = self.tree.AddRoot("My Computers") #os.path.basename(path))
        # self.tree.SetItemData(self.root, None)
        # self.tree.SetItemImage(self.root, self.fldridx, wx.TreeItemIcon_Normal)
        # self.tree.SetItemImage(self.root, self.fldropenidx, wx.TreeItemIcon_Expanded)









        '''
        for item in paths:
            if os.path.isdir(path+item):
                print 'yes'
                child = self.tree.AppendItem(self.root,os.path.basename(item))
                self.tree.SetItemData(child, None)
                #self.tree.SetItemImage(child, fldridx, wx.TreeItemIcon_Normal)
                self.tree.SetItemImage(child, fldridx, wx.TreeItemIcon_Expanded)
                else:
                    print 'no'
                    last = self.tree.AppendItem(self.root, os.path.basename(path+item))
                    self.tree.SetItemData(last, None)
                    self.tree.SetItemImage(last, fileidx, wx.TreeItemIcon_Normal)
                    #self.tree.SetItemImage(child, fldropenidx, wx.TreeItemIcon_Expanded)
        '''
        for x in range(7):
            if x!=6:
                child = self.tree.AppendItem(self.root, "Item %d" % x)
                self.tree.SetItemData(child, None)
                self.tree.SetItemImage(child, self.fldridx, wx.TreeItemIcon_Normal)
                self.tree.SetItemImage(child, self.fldropenidx, wx.TreeItemIcon_Expanded)

                for y in range(5):
                    last = self.tree.AppendItem(child, "item %d-%s" % (x, chr(ord("a")+y)))
                    self.tree.SetItemData(last, None)
                    self.tree.SetItemImage(last, self.fileidx, wx.TreeItemIcon_Normal)
            else:
                child = self.tree.AppendItem(self.root, "Item %d" % x)
                self.tree.SetItemData(child, None)
                self.tree.SetItemImage(child, self.fldridx, wx.TreeItemIcon_Normal)
                self.tree.SetItemImage(child, self.fldropenidx, wx.TreeItemIcon_Expanded)


        self.tree.Expand(self.root)




        result = self.get_item_by_label( 'item 0-d', self.tree.GetRootItem())
        if result.IsOk():
            print('We have a match!')
            child = self.tree.AppendItem(result, "Shchar")
            self.tree.SetItemData(child, None)
            self.tree.SetItemImage(child, self.fldridx, wx.TreeItemIcon_Normal)



        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onTreeDClick, self.tree)

    def onTreeDClick(self,event):
        print('Double clicked on', self.tree.GetItemText(event.GetItem()))




    def get_item_by_label(self, search_text, root_item):
        item, cookie = self.tree.GetFirstChild(root_item)

        while item.IsOk():
            text = self.tree.GetItemText(item)
            if text.lower() == search_text.lower():
                return item
            if self.tree.ItemHasChildren(item):
                match = self.get_item_by_label(search_text, item)
                if match.IsOk():
                    return match
            item, cookie = self.tree.GetNextChild(root_item, cookie)

        return wx.TreeItemId()


    def get_my_item(self,search_text):
        name = "The Root Item/Item 0/item0-d"
        names = name.split("/")
        start_root = self.tree.GetRootItem()

        i=0
        x = names[i]
        newTree = self.get_item_by_label(x,start_root)
        while newTree:
            start_root = newTree
            i += 1
            if i < len(names):
                newTree = self.get_item_by_label(x[i],start_root)
            else:
                if i == len(names)-1: #last
                    child = self.tree.AppendItem(start_root, x[i])
                    self.tree.SetItemData(child, None)
                    self.tree.SetItemImage(child, self.fldridx, wx.TreeItemIcon_Normal)
                else:
                    child = self.tree.AppendItem(start_root, x[i])
                    self.tree.SetItemData(child, None)
                    self.tree.SetItemImage(child, self.fldridx, wx.TreeItemIcon_Normal)
                    self.tree.SetItemImage(child, self.fldropenidx, wx.TreeItemIcon_Expanded)


########################################################################
class MyFrame(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(MyFrame, self).__init__(None, title="TreeCtrl Example")
        panel = MyPanel(self)
        self.Show()

if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame()
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()