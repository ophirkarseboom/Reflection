import wx
from typing import Dict
import os
from Reflection.file_stuff.file_handler import FileHandler
from Reflection.protocols import user_client_protocol as protocol


class TestFrame(wx.Frame):

    open_folder_name = 'open_folder.png'
    close_folder_name = 'close_folder.png'
    file_name = 'file.png'

    def __init__(self):
        wx.Frame.__init__(self, None, -1)
        self.cwd = os.getcwd() + '\\'
        self.tree = wx.TreeCtrl(self, style=wx.TR_HIDE_ROOT)
        self.root = self.tree.AddRoot("root")
        self.image_list = wx.ImageList(16, 16)
        self.tree.AssignImageList(self.image_list)
        dic = {'C:\\reflection\\yotam': ['10.100.102.19', '10.100.102.27', ','], 'C:\\reflection\\yotam\\10.100.102.27': ['folder1', 'folder2', 'folder5', ',', 'doc.txt'], 'C:\\reflection\\yotam\\10.100.102.27\\folder1': [','], 'C:\\reflection\\yotam\\10.100.102.27\\folder2': [',', 'a.txt'], 'C:\\reflection\\yotam\\10.100.102.27\\folder5': [',', 'a.txt'], 'C:\\reflection\\yotam\\10.100.102.19': ['folder1', 'folder2', 'folder3', 'folder4', 'folder5', 'folder6', 'folder7', 'folder8', ',', 'a.py', 'a.txt', 'b.txt', 'c.txt', 'k.txt'], 'C:\\reflection\\yotam\\10.100.102.19\\folder1': [',', 'a.txt'], 'C:\\reflection\\yotam\\10.100.102.19\\folder2': [','], 'C:\\reflection\\yotam\\10.100.102.19\\folder3': [',', 'a.txt'], 'C:\\reflection\\yotam\\10.100.102.19\\folder4': [','], 'C:\\reflection\\yotam\\10.100.102.19\\folder5': [',', 'a.txt'], 'C:\\reflection\\yotam\\10.100.102.19\\folder6': [',', 'a.txt'], 'C:\\reflection\\yotam\\10.100.102.19\\folder7': [',', 'a.txt'], 'C:\\reflection\\yotam\\10.100.102.19\\folder8': [',', 'a.txt']}
        self.convertToTree(dic)

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivated, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed, self.tree)

    def convertToTree(self, dic: dict, father=None):
        """
        gets dictionary and converts it to tree
        :param dic: dictionary
        :param father: a parent
        :return: None
        """

        if not father:
            father_path = next(iter(dic.keys()))
            father = self.root
        else:
            father_path = self.tree.GetItemData(father)

        folder = True
        if father_path not in dic:
            return

        # runs on every object in this folder adds it to tree and if is folder then
        for element in dic[father_path]:
            if element == ',':
                folder = False
                continue

            new_item = self.tree.AppendItem(father, element, data=f'{father_path}\\{element}')
            self.add_pic(new_item, element, folder)
            if folder:

                self.convertToTree(dic, new_item)

    def add_pic(self, item, name: str, is_folder: bool):
        """
        gets item and adds correct image to it
        :param item: object in tree
        :param name: name of item
        :return: None
        """
        name = name.split('.')
        if is_folder:
            pic_name = self.close_folder_name
        else:
            pic_name = self.file_name

        item_image = self.image_list.Add(wx.Image(self.cwd + pic_name, wx.BITMAP_TYPE_PNG).Scale(16, 16).ConvertToBitmap())
        self.tree.SetItemImage(item, item_image, wx.TreeItemIcon_Normal)



    def OnActivated(self, evt):

        print("hello")
        print('Double clicked on', self.tree.GetItemData(evt.GetItem()))
        item = evt.GetItem()
        if self.tree.IsExpanded(item):
            self.tree.Collapse(item)
        else:
            self.tree.Expand(item)

    def OnItemExpanded(self, evt):
        item = evt.GetItem()
        print('Double clicked on', self.tree.GetItemData(item))

        item_image = self.image_list.Add(wx.Image(self.cwd + self.open_folder_name, wx.BITMAP_TYPE_PNG).Scale(16, 16).ConvertToBitmap())
        self.tree.SetItemImage(item, item_image, wx.TreeItemIcon_Normal)

    def OnItemCollapsed(self, evt):
        item = evt.GetItem()
        item_image = self.image_list.Add(wx.Image(self.cwd + self.close_folder_name, wx.BITMAP_TYPE_PNG).Scale(16, 16).ConvertToBitmap())
        self.tree.SetItemImage(item, item_image, wx.TreeItemIcon_Normal)


if __name__ == "__main__":
    a = wx.App(False)
    f = TestFrame()
    f.Show()
    a.MainLoop()