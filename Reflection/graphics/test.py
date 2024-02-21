import wx
from typing import Dict
import os
from Reflection.file_stuff.file_handler import FileHandler
from Reflection.protocols import user_client_protocol as protocol


class TestFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1)

        self.tree = wx.TreeCtrl(self, style=wx.TR_HIDE_ROOT)
        self.root = self.tree.AddRoot("root")
        self.image_list = wx.ImageList(16, 16)
        print(protocol.unpack('05'+FileHandler.get_path_tree('T:\public\cyber\ophir\Reflection\Reflection'))[1][0])
        dic = {'D:\\reflection\\yotam': ['192.168.4.96', ','], 'D:\\reflection\\yotam\\192.168.4.96': ['folder', 'folder1', 'folder10', 'folder2', 'folder3', 'folder4', 'folder5', 'folder6', 'folder7', ',', 'file.txt', 'hi.docx'], 'D:\\reflection\\yotam\\192.168.4.96\\folder': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder1': ['in1', ','], 'D:\\reflection\\yotam\\192.168.4.96\\folder1\\in1': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder10': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder2': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder3': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder4': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder5': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder6': ['folder_in_6', ',', 'a.txt'], 'D:\\reflection\\yotam\\192.168.4.96\\folder6\\folder_in_6': [','], 'D:\\reflection\\yotam\\192.168.4.96\\folder7': [',', 'a.txt', 'b.txt']}
        dic = protocol.unpack('05'+FileHandler.get_path_tree('T:\public\cyber\ophir\Reflection\Reflection'))[1][0]
        self.convertToTree(dic)


        # self.root = self.tree.AddRoot("")
        # gr = self.tree.AppendItem(self.root, "Grooveshark", data='nice')
        # pop_r = self.tree.AppendItem(gr, "Popular")
        # sr = self.tree.AppendItem(gr, "Search")
        #
        # dr = self.tree.AppendItem(self.root, "Download")
        #
        # pr = self.tree.AppendItem(self.root, "Pandora")
        # stat_r = self.tree.AppendItem(pr, "Stations")




        # grooveshark = image_list.Add(wx.Image(r"T:\public\cyber\ophir\Reflection\Reflection\graphics\image.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
        # popular     = image_list.Add(wx.Image(r"T:\public\cyber\ophir\Reflection\Reflection\graphics\image.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
        # search      = image_list.Add(wx.Image(r"T:\public\cyber\ophir\Reflection\Reflection\graphics\image.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
        # download    = image_list.Add(wx.Image(r"T:\public\cyber\ophir\Reflection\Reflection\graphics\image.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
        # pandora     = image_list.Add(wx.Image(r"T:\public\cyber\ophir\Reflection\Reflection\graphics\image.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
        # stations    = image_list.Add(wx.Image(r"T:\public\cyber\ophir\Reflection\Reflection\graphics\image.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
        #
        # self.tree.AssignImageList(image_list)

        # self.tree.SetItemImage(gr, grooveshark, wx.TreeItemIcon_Normal)
        # self.tree.SetItemImage(pop_r, popular, wx.TreeItemIcon_Normal)
        # self.tree.SetItemImage(sr, search, wx.TreeItemIcon_Normal)
        # self.tree.SetItemImage(dr, download, wx.TreeItemIcon_Normal)
        # self.tree.SetItemImage(pr, pandora, wx.TreeItemIcon_Normal)
        # self.tree.SetItemImage(stat_r, stations, wx.TreeItemIcon_Normal)
        #
        # self.tree.SetItemData(pop_r, 2)
        #
        # self.tree.SetItemData(sr, 3)
        #
        # self.tree.SetItemData(dr, 4)
        #
        # self.tree.SetItemData(pr, 5)
        #
        # self.tree.SetItemData(stat_r, 6)
        #

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
        # dic = {'D:\\reflection\\yotam\\': ['192.168.4.96', ','],
        #        'D:\\reflection\\yotam\\192.168.4.96': ['folder', 'folder1', 'folder10', 'folder2', 'folder3', 'folder4',
        #                                                'folder5', 'folder6', 'folder7', ',', 'file.txt', 'hi.docx'],
        #        'D:\\reflection\\yotam\\192.168.4.96\\folder': [','],
        #        'D:\\reflection\\yotam\\192.168.4.96\\folder1': ['in1', ','],
        #        'D:\\reflection\\yotam\\192.168.4.96\\folder1\\in1': [','],
        #        'D:\\reflection\\yotam\\192.168.4.96\\folder10': [','],
        #        'D:\\reflection\\yotam\\192.168.4.96\\folder2': [','],
        #        'D:\\reflection\\yotam\\192.168.4.96\\folder3': [','],
        #        'D:\\reflection\\yotam\\192.168.4.96\\folder4': [','],
        #        'D:\\reflection\\yotam\\192.168.4.96\\folder5': [','],
        #        'D:\\reflection\\yotam\\192.168.4.96\\folder6': ['folder_in_6', ',', 'a.txt'],
        #        'D:\\reflection\\yotam\\192.168.4.96\\folder6\\folder_in_6': [','],
        #        'D:\\reflection\\yotam\\192.168.4.96\\folder7': [',', 'a.txt', 'b.txt']}
        if not father:
            father_path = next(iter(dic.keys()))
            father = self.tree.AppendItem(self.root, os.path.basename(father_path), data=father_path)
        else:
            father_path = self.tree.GetItemData(father)

        print('father_path:', father_path)
        folder = True
        if father_path not in dic:
            print('hi')
            return
        for element in dic[father_path]:
            if element == ',':
                folder = False
                continue

            new_item = self.tree.AppendItem(father, element, data=f'{father_path}\\{element}')
            if folder:
                # self.add_pic(new_item, element)
                self.convertToTree(dic, new_item)










        # results: Dict[str, wx.TreeItemId] = {"" : root}
        # for dir, files in dic.items():
        #     sub_dirs = dir.split("\\")
        #     temp = ""
        #
        #     for sub_dir in sub_dirs:
        #         old_temp = temp
        #         temp += sub_dir
        #         if temp not in results:
        #             new_child = self.tree.AppendItem(results[old_temp], " ".join(files))
        #             results[temp] = new_child
        #
        # print(results)



    def add_pic(self, item, name: str):
        """
        gets item and adds correct image to it
        :param item: object in tree
        :param name: name of item
        :return: None
        """
        pic_path = 'T:\\public\\cyber\\ophir\\Reflection\\Reflection\\graphics\\'
        name = name.split()
        if len(name) == 1:
            pic_path += 'folder.png'
        else:
            # pic_path += name[1]
            pic_path += 'folder.png'

        item_image = self.image_list.Add(wx.Image(pic_path, wx.BITMAP_TYPE_PNG).Scale(16, 16).ConvertToBitmap())
        self.tree.AssignImageList(self.image_list)
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
        print("hello")
        print('Double clicked on', self.tree.GetItemData(evt.GetItem()))


    def OnItemCollapsed(self, evt):
        print("hello")
        print('Double clicked on', self.tree.GetItemData(evt.GetItem()))


if __name__ == "__main__":
    a = wx.App(False)
    f = TestFrame()
    f.Show()
    a.MainLoop()