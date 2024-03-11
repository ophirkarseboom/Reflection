import time
import wx
brown = wx.Colour(165, 132, 82)
import os
from pubsub import pub
from Reflection import settings
from queue import Queue
from Reflection.graphics import notification
from Reflection.local_handler.file_handler import FileHandler
import sys


class CreateFileDialog(wx.Dialog):
    def __init__(self, parent, title: str, is_folder):

        super(CreateFileDialog, self).__init__(parent, title=title, size=(300, 150))
        self.is_folder = is_folder

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
        self.EndModal(wx.ID_OK)


    def on_cancel(self, event):
        """
        closes file dialog
        :param event: event happened
        """
        self.EndModal(wx.ID_CANCEL)



class TreeFrame(wx.Frame):
    open_folder_name = 'open_folder.png'
    close_folder_name = 'fld.png'
    file_name = 'txt.png'
    image_types = ["apng", "avif", "gif", "jpg", "jpeg", "jfif", "pjpeg", "pjp", "png", "svg", "webp", "bmp", "ico",
                   "cur",
                   "tif", "tiff"]
    def __init__(self, parent, command_q: Queue):
        # wx.Panel.__init__(self, parent, -1)
        wx.Frame.__init__(self, parent, pos=wx.DefaultPosition)
        self.cwd = settings.Settings.pic_path
        self.tree = wx.TreeCtrl(self, style=wx.TR_HIDE_ROOT)
        self.file_commands = ('open', 'delete', 'rename', 'download')
        self.folder_commands = ('create file', 'create folder', 'delete', 'rename', 'upload file')
        self.root = self.tree.AddRoot("root")
        self.command_q = command_q
        self.folders = []
        self.image_list = wx.ImageList(16, 16)
        self.tree.AssignImageList(self.image_list)
        self.path_item = {}
        self.forbidden = ('*', ',', '\\', '/', '[', ']', '{', '}', '?', '<', '>', ' ', ':', '|')

        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_double_clicked)
        self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.on_expanded)
        self.tree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.on_collapsed)
        self.tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_right_click)
        self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_drag)
        self.tree.Bind(wx.EVT_TREE_END_DRAG, self.stop_drag)

        pub.subscribe(self.convert_to_tree, "update_tree")
        pub.subscribe(self.add_object, "create")
        pub.subscribe(self.delete_object, "delete")
        pub.subscribe(notification.show_error, "error")

        self.Show()

    def stop_drag(self, evt):
        draged_on = evt.GetItem()
        print('draged_on:', self.tree.GetItemData(draged_on))

    def on_drag(self, evt):

        evt.Allow()
        self.drag_item = self.tree.GetItemData(evt.GetItem())

        print(self.drag_item)

    def valid_input(self, file_name: str, is_folder: bool):
        """
        check if input is up to standard
        :return: if input is valid or not
        """
        valid = True
        # temp
        forbidden = list(self.forbidden)

        if is_folder:
            forbidden.append('.')
        else:
            valid = file_name.count('.') == 1
        for bad in forbidden:
            if bad in file_name or not valid:
                valid = False
                break

        if len(file_name) > 30:
            valid = False
        return valid


    def create_file_dialog(self, command: str, path: str):
        """
        creates file dialog and sends answer to logic
        :param command: command
        :param path:
        :return:
        """
        dialog_title = command + ' '
        if command.startswith('create'):
            dialog_title += f'in {os.path.basename(path)}:'
            is_folder = command.endswith('folder')
        elif command == 'rename':
            dialog_title += f'{os.path.basename(path)} to:'
            is_folder = path in self.folders

        else:
            # temp
            is_folder = False
        while True:
            dialog = CreateFileDialog(self, dialog_title.capitalize(), is_folder)
            if dialog.ShowModal() == wx.ID_OK:
                file_name = dialog.file_name
                full_path = f'{path}\\{file_name}'
                if not self.valid_input(file_name, is_folder):
                    notification.show_error(f'name "{file_name}" is not valid')
                elif full_path in self.path_item:
                    notification.show_error(f'"{file_name}" already exists in this directory')
                else:
                    self.command_q.put((command, full_path))
                    break
            else:
                break
        dialog.Destroy()

    def delete_object(self, path: str):
        """
        gets path of object and deletes it from needed places
        :param path: path of object
        """
        if path in self.path_item:
            self.tree.Delete(self.path_item[path])

    def add_object(self, path: str, name: str, typ: str):
        """
        adds object to tree
        :param path: path of file (directory above it)
        :param name: name of file
        :param typ: type of file\folder
        """
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
        for command in commands:
            self.popupmenu.Append(-1, command)
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
        if text.startswith('create') or text == 'rename':
            self.create_file_dialog(text, path)
        elif text == 'upload file' or text == 'download':
            file_dialog = wx.FileDialog(None, "Choose a file", style=wx.FD_OPEN)
            file_explorer_path_chose = None
            if file_dialog.ShowModal() == wx.ID_OK:
                file_explorer_path_chose = file_dialog.GetPath()
                print("Selected file:", file_explorer_path_chose)

            file_dialog.Destroy()
            if file_explorer_path_chose:
                self.command_q.put((text, f'{path},{file_explorer_path_chose}'))
        else:
            self.command_q.put((text, path))

    def convert_to_tree(self, dic: dict, father=None):
        """
        gets dictionary and converts it to tree
        :param dic: dictionary
        :param father: a parent
        :return: None
        """

        if not father:
            print('dictionary working with:', dic)
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

        if is_folder:
            pic_name = self.close_folder_name
        else:

            name, typ = name.split('.')
            pic_name = typ
            if typ in TreeFrame.image_types:
                pic_name = 'pic'
            pic_name += '.png'
            if pic_name not in os.listdir(settings.Settings.pic_path):
                pic_name = 'txt.png'
        item_image = self.image_list.Add(
            wx.Image(self.cwd + pic_name, wx.BITMAP_TYPE_PNG).Scale(16, 16).ConvertToBitmap())
        self.tree.SetItemImage(item, item_image, wx.TreeItemIcon_Normal)

    def on_double_clicked(self, evt):
        """
        gets evt and does stuff for double clicked
        :param evt: event happened
        :return: None
        """
        item = evt.GetItem()
        path = self.tree.GetItemData(item)
        if path in self.folders:
            if self.tree.IsExpanded(item):
                self.tree.Collapse(item)
            else:
                self.tree.Expand(item)

        # open file
        else:
            self.command_q.put(('open', path))
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

        self.SetClientSize(self.GetBestSize())
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
        self.SetClientSize(self.GetBestSize())



if __name__ == '__main__':
    app = wx.App(False)
    first = TreeFrame(None, Queue())
    app.MainLoop()
