import time
import wx
brown = wx.Colour(165, 132, 82)
import os
from pubsub import pub
from Reflection import settings
from queue import Queue
from Reflection.graphics import notification

class CreateFileDialog(wx.Dialog):
    def __init__(self, parent, title: str):
        super(CreateFileDialog, self).__init__(parent, title=title, size=(300, 150))

        self.is_folder = title.lower().endswith('folder')
        self.forbidden = ('*', ',', '\\', '/', '[', ']', '{', '}', '?', '<', '>', ' ', ':', '|')
        self.file_name = ''
        self.panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        text_box = wx.BoxSizer(wx.HORIZONTAL)
        lbl = wx.StaticText(self.panel, label="Enter Name:")
        text_box.Add(lbl, flag=wx.RIGHT, border=8)
        self.text_ctrl = wx.TextCtrl(self.panel)
        text_box.Add(self.text_ctrl, proportion=1)
        vbox.Add(text_box, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(self.panel, label='OK')
        btn_ok.Bind(wx.EVT_BUTTON, self.on_ok)
        btn_box.Add(btn_ok)
        btn_cancel = wx.Button(self.panel, label='Cancel')
        btn_cancel.Bind(wx.EVT_BUTTON, self.on_cancel)
        btn_box.Add(btn_cancel, flag=wx.LEFT, border=5)
        vbox.Add(btn_box, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        self.panel.SetSizer(vbox)

    def on_ok(self, event):
        """
        when pressed on ok gets input and tells if valid or not
        :param event: event happened
        """
        self.file_name = self.text_ctrl.GetValue()
        if self.valid_input():
            self.EndModal(wx.ID_OK)
        else:
            notification.show_error('name is not valid')


    def on_cancel(self, event):
        """
        closes file dialog
        :param event: event happened
        """
        self.EndModal(wx.ID_CANCEL)

    def valid_input(self):
        """
        check if input is up to standard
        :return: if input is valid or not
        """
        valid = True

        # temp
        forbidden = list(self.forbidden)
        if self.is_folder:
            forbidden.append('.')
        else:
            valid = self.file_name.count('.') == 1
        for bad in forbidden:
            if bad in self.file_name or not valid:
                valid = False
                break

        return valid


class TreePanel(wx.Frame):
    open_folder_name = 'open_folder.png'
    close_folder_name = 'close_folder.png'
    file_name = 'file.png'

    def __init__(self, parent, command_q: Queue):
        # wx.Panel.__init__(self, parent, -1)
        wx.Frame.__init__(self, parent, pos=wx.DefaultPosition)
        self.cwd = settings.Settings.pic_path
        self.tree = wx.TreeCtrl(self, style=wx.TR_HIDE_ROOT)
        self.file_commands = ('open', 'delete', 'rename')
        self.folder_commands = ('create file', 'create folder', 'delete', 'rename')
        self.root = self.tree.AddRoot("root")
        self.command_q = command_q
        self.folders = []
        self.image_list = wx.ImageList(16, 16)
        self.tree.AssignImageList(self.image_list)
        self.path_item = {}

        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_double_clicked)
        self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.on_expanded)
        self.tree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.on_collapsed)
        self.tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_right_click)

        pub.subscribe(self.convert_to_tree, "update_tree")
        pub.subscribe(self.add_object, "create")
        pub.subscribe(self.delete_object, "delete")
        pub.subscribe(notification.show_error, "error")

        self.Show()

    def create_file_dialog(self, text: str, path: str):
        """
        creates file dialog and sends answer to logic
        :param text: command
        :param path:
        :return:
        """
        dialog = CreateFileDialog(self, text.upper())
        if dialog.ShowModal() == wx.ID_OK:
            file_name = dialog.file_name
            self.command_q.put((text, f'{path}\\{file_name}'))
        dialog.Destroy()

    def delete_object(self, path: str):
        """
        gets path of object and deletes it from needed places
        :param path: path of object
        """
        if path in self.path_item:
            self.tree.Delete(self.path_item[path])

    def add_object(self, path: str, name: str, typ: str):
        if path not in self.path_item:
            return

        dir_on = self.path_item[path]
        if typ == 'fld':
            full_path = f'{path}\\{name}'
            new_item = self.tree.AppendItem(dir_on, f'{name}', data=full_path)
            self.path_item[full_path] = new_item
            self.folders.append(full_path)
            self.add_pic(new_item, name, True)
        else:
            full_path = f'{path}\\{name}.{typ}'
            new_item = self.tree.AppendItem(dir_on, f'{name}.{typ}', data=full_path)
            self.path_item[full_path] = new_item
            self.add_pic(new_item, f'{name}.{typ}', False)


    def on_right_click(self, evt):
        """
        gets evt and does stuff for right click
        :param evt: event happened
        :return: None
        """
        item = evt.GetItem()
        item_path = self.tree.GetItemData(item)
        if item_path in self.folders:
            commands = self.folder_commands
        else:
            commands = self.file_commands

        self.popupmenu = wx.Menu()
        item_name = os.path.basename(item_path)
        self.popupmenu.SetTitle(f'{item_name}:')
        for text in commands:
            self.popupmenu.Append(-1, text)
            self.Bind(wx.EVT_MENU, lambda event, item_pressed=item: self.command_selected(event, item_pressed))

        self.PopupMenu(self.popupmenu)

    def command_selected(self, evt: wx.CommandEvent, item):
        """
        gets event and item and informs logic which command was chosen and on what
        :param evt: event happened
        :param item: item pressed on
        :return: None
        """
        id_selected = evt.GetId()
        obj = evt.GetEventObject()
        text = obj.GetLabel(id_selected)
        path = self.tree.GetItemData(item)
        if text.startswith('create'):
            self.create_file_dialog(text, path)
        else:
            self.command_q.put((text, path))

    def convert_to_tree(self, dic: dict, father=None):
        """
        gets dictionary and converts it to tree
        :param dic: dictionary
        :param father: a parent
        :return: None
        """
        print('dict:', dic)
        if not father:
            father_path = next(iter(dic.keys()))
            father = self.root
        else:
            father_path = self.tree.GetItemData(father)

        folder = True
        print('father path:', father_path)
        if father_path not in dic:
            return

        # runs on every object in this folder adds it to tree and if is folder then
        for element in dic[father_path]:
            if element == ',':
                folder = False
                continue

            path = f'{father_path}\\{element}'
            new_item = self.tree.AppendItem(father, element, data=path)
            self.path_item[path] = new_item
            self.add_pic(new_item, element, folder)

            if folder:
                self.folders.append(path)
                self.convert_to_tree(dic, new_item)


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

        item_image = self.image_list.Add(
            wx.Image(self.cwd + pic_name, wx.BITMAP_TYPE_PNG).Scale(16, 16).ConvertToBitmap())
        self.tree.SetItemImage(item, item_image, wx.TreeItemIcon_Normal)

    def on_double_clicked(self, evt):
        """
        gets evt and does stuff for double clicked
        :param evt: event happened
        :return: None
        """
        print("hello")
        print('Double clicked on', self.tree.GetItemData(evt.GetItem()))
        print(self.path_item)
        item = evt.GetItem()
        if self.tree.IsExpanded(item):
            self.tree.Collapse(item)
        else:
            self.tree.Expand(item)

    def on_expanded(self, evt):
        """
        gets evt and does stuff for expanded item
        :param evt: event happened
        :return: None
        """
        item = evt.GetItem()

        item_image = self.image_list.Add(
            wx.Image(self.cwd + self.open_folder_name, wx.BITMAP_TYPE_PNG).Scale(16, 16).ConvertToBitmap())
        self.tree.SetItemImage(item, item_image, wx.TreeItemIcon_Normal)

    def on_collapsed(self, evt):
        """
       gets evt and does stuff for collapsed item
       :param evt: event happened
       :return: None
       """
        item = evt.GetItem()
        item_image = self.image_list.Add(
            wx.Image(self.cwd + self.close_folder_name, wx.BITMAP_TYPE_PNG).Scale(16, 16).ConvertToBitmap())
        self.tree.SetItemImage(item, item_image, wx.TreeItemIcon_Normal)



if __name__ == '__main__':
    app = wx.App(False)
    first = TreePanel(None, Queue())
    app.MainLoop()