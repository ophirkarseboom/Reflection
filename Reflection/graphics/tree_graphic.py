
import wx
import os
from pubsub import pub
from Reflection import settings
from queue import Queue
from Reflection.local_handler.file_handler import FileHandler
from Reflection.settings import Settings

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
        wx.Frame.__init__(self, parent, pos=wx.DefaultPosition, size=(500, 500))
        self.cwd = settings.Settings.pic_path
        self.tree = wx.TreeCtrl(self, style=wx.TR_HIDE_ROOT)
        self.file_commands = ('open', 'delete', 'rename', 'download', 'copy')
        self.folder_commands = ('create file', 'create folder', 'delete', 'rename', 'upload file', 'paste')
        self.root = self.tree.AddRoot("root")
        self.command_q = command_q
        self.folders = []
        self.image_size = 16
        self.item_image_path = {}
        self.image_list = wx.ImageList(self.image_size, self.image_size)
        self.tree.AssignImageList(self.image_list)
        self.path_item = {}
        self.forbidden = ('*', ',', '\\', '/', '[', ']', '{', '}', '?', '<', '>', ' ', ':', '|', '(', ')', '-')
        self.on_clipboard_path = None
        self.loading_cursor = wx.Cursor(wx.CURSOR_WAIT)

        self.my_ip = Settings.get_ip()

        self.font = wx.Font(round(self.image_size * 0.7), wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.tree.SetFont(self.font)
        self.tree.SetForegroundColour(wx.Colour(255, 255, 255))

        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_double_clicked)
        self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.on_expanded)
        self.tree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.on_collapsed)
        self.tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_right_click)
        self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_drag)
        self.tree.Bind(wx.EVT_TREE_END_DRAG, self.on_drop)
        self.tree.Bind(wx.EVT_CHAR_HOOK, self.copy_paste)
        self.tree.Bind(wx.EVT_MOUSEWHEEL, self.change_size)

        self.SetIcon(wx.Icon(settings.Settings.icon_path))
        pub.subscribe(self.convert_to_tree, "update_tree")
        pub.subscribe(self.add_object, "create")
        pub.subscribe(self.delete_object, "delete")
        pub.subscribe(self.show_error, "error")
        pub.subscribe(self.rename_object, "rename")
        pub.subscribe(self.refresh_cursor, "cursor")

        self.tree.SetBackgroundColour(wx.Colour(30, 30, 30))
        self.Show()



    def refresh_cursor(self):
        """
        refreshes cursor after finishing action
        """
        self.SetCursor(wx.Cursor())

    def send_to_logic(self, command: str, data: str):
        """
        sends to logic data
        :param command: the command the logic should do with the data
        :param data: the data delivered with the command
        :return None
        """
        my_cursor = wx.Cursor(wx.CURSOR_WAIT)
        self.SetCursor(my_cursor)
        self.command_q.put((command, data))


    def change_size(self, evt: wx.MouseEvent):
        """
        changes size of font and pictures
        :param evt: mouse scroll up or down
        :return: None
        """
        if not evt.CmdDown():
            evt.Skip()
            return

        # bounds
        if self.image_size < 10 or self.image_size > 30:
            if self.image_size < 10:
                self.image_size = 10
            else:
                self.image_size = 30

        if evt.GetWheelRotation() > 0:
            self.image_size += 1
        else:
            self.image_size -= 1

        # changing font
        self.font.SetPointSize(self.image_size)
        self.tree.SetFont(self.font)

        self.image_list = wx.ImageList(self.image_size, self.image_size)
        self.tree.AssignImageList(self.image_list)

        # resizing every image
        for item in self.item_image_path:
            path = self.item_image_path[item]
            result = wx.Bitmap(path)
            image = result.ConvertToImage()
            image = image.Scale(self.image_size, self.image_size, wx.IMAGE_QUALITY_HIGH)
            image = self.image_list.Add(image.ConvertToBitmap())
            self.tree.SetItemImage(item, image, wx.TreeItemIcon_Normal)



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
            print(name)
            typ_index = name.rfind('.')
            typ = name[typ_index + 1:]
            pic_name = typ
            if typ in TreeFrame.image_types:
                pic_name = 'pic'
            pic_name += '.png'
            if pic_name not in os.listdir(settings.Settings.pic_path):
                pic_name = 'txt.png'

        pic_path = self.cwd + pic_name
        self.put_pic_for_item(pic_path, item)

    def put_pic_for_item(self, pic_path: str, item: wx.TreeItemId):
        """
        changes pic for certain item
        :param pic_path: path of the pic
        :param item: the item in tree
        :return: None
        """
        item_image = wx.Image(pic_path, wx.BITMAP_TYPE_PNG).Scale(self.image_size, self.image_size)
        self.item_image_path[item] = pic_path
        item_image = item_image.ConvertToBitmap()
        item_image = self.image_list.Add(item_image)
        self.tree.SetItemImage(item, item_image, wx.TreeItemIcon_Normal)


    def on_expanded(self, evt):
        """
        gets evt and does stuff for expanded item
        :param evt: event happened
        :return: None
        """
        item = evt.GetItem()
        pic_path = self.cwd + self.open_folder_name
        self.put_pic_for_item(pic_path, item)

    def on_collapsed(self, evt):
        """
       gets evt and does stuff for collapsed item
       :param evt: event happened
       :return: None
       """
        item = evt.GetItem()
        pic_path = self.cwd + self.close_folder_name
        self.put_pic_for_item(pic_path, item)

    def copy_paste(self, evt: wx.KeyEvent):
        """
        get key pressed and tells logic if got copy or paste
        :param evt: key event
        :return: None
        """
        key_code = evt.GetKeyCode()
        ctrl_down = evt.CmdDown()
        if ctrl_down:

            # copy
            if key_code == 67:
                on_item = self.tree.GetFocusedItem()
                on_item_path = self.tree.GetItemData(on_item)
                print('copy')
                if on_item_path in self.folders:
                    self.show_error('cannot copy folder')
                else:
                    self.on_clipboard_path = on_item_path

            # paste
            elif key_code == 86:
                on_item = self.tree.GetFocusedItem()
                on_item_path = self.tree.GetItemData(on_item)
                print('paste')
                if self.on_clipboard_path:
                    self.send_to_logic('paste', f'{self.on_clipboard_path},{on_item_path}')

    def on_drop(self, evt):
        """
        tells graphic when drag stopped and where
        :param evt: event got
        :return: None
        """
        self.refresh_cursor()
        dropped_on = self.tree.GetItemData(evt.GetItem())
        dragged_data = self.tree.GetItemData(self.drag_item)
        self.send_to_logic('move', f'{dragged_data},{dropped_on}')

    def on_drag(self, evt):
        """
        lets drag start visually and keeps item dragged
        :param evt: event got
        :return: None
        """
        evt.Allow()
        self.drag_item = evt.GetItem()
        cursor = wx.Cursor(wx.Image(self.item_image_path[self.drag_item]))
        self.SetCursor(cursor)
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
                full_path = os.path.join(path, file_name)
                print('full_path:', full_path)
                if not self.valid_input(file_name, is_folder):
                    self.show_error(f'name "{file_name}" is not valid')
                elif full_path in self.path_item:
                    self.show_error(f'"{file_name}" already exists in this directory')
                else:
                    self.send_to_logic(command, full_path)
                    break
            else:
                break
        dialog.Destroy()

    def rename_object(self, old_path: str, new_name: str):
        """
        renames an object in the tree
        :param old_path: the old path of the object
        :param new_name: the new name of the object
        :return if success in renaming object
        """
        worked = old_path in self.path_item
        if worked:
            item = self.path_item[old_path]
            self.tree.SetItemText(item, new_name)

            folder_path, _ = FileHandler.split_path_last_part(old_path)
            new_path = os.path.join(folder_path, new_name)

            to_add = {}
            to_remove = []
            for path in self.path_item.keys():
                print('path:    ', path)
                print('old_path:', old_path)
                if path.startswith(old_path):
                    print('got in')
                    item = self.path_item[path]
                    to_remove.append(path)
                    replaced_path = path.replace(old_path, new_path, 1)
                    print('replaced_path:', replaced_path)
                    to_add[replaced_path] = item
                    self.tree.SetItemData(item, replaced_path)

                print()
            for path in to_add:
                self.path_item[path] = to_add[path]

            for path in to_remove:
                del self.path_item[path]

            print('path_item_before:', self.path_item.keys())
            print('path_item_after:', self.path_item.keys())
            # is folder
            if '.' not in new_name:
                self.folders.remove(old_path)
                self.folders.append(new_path)

        return worked

    def delete_object(self, path: str):
        """
        gets path of object and deletes it from needed places
        :param path: path of object
        """
        if path in self.path_item:
            self.tree.Delete(self.path_item[path])
            del self.path_item[path]

    def add_object(self, path: str, name: str, typ: str):
        """
        adds object to tree
        :param path: path of file (directory above it)
        :param name: name of file
        :param typ: type of file\folder
        """
        print(f'path: {path}')
        print(f'path_item: {self.path_item}')
        if path not in self.path_item:
            return

        dir_on = self.path_item[path]
        full_path = os.path.join(path, name)
        if typ == 'fld':

            new_item = self.tree.AppendItem(dir_on, f'{name}', data=full_path)
            self.path_item[full_path] = new_item
            self.folders.append(full_path)
            self.add_pic(new_item, name, True)
        else:
            full_path = f'{full_path}.{typ}'
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
        self.tree.SetFocusedItem(item)
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
                self.send_to_logic(text, f'{path},{file_explorer_path_chose}')

        elif text == 'paste':
            on_item = self.tree.GetFocusedItem()
            on_item_path = self.tree.GetItemData(on_item)
            if self.on_clipboard_path:
                self.send_to_logic(text, f'{self.on_clipboard_path},{on_item_path}')

        elif text == 'copy':
            on_item = self.tree.GetFocusedItem()
            on_item_path = self.tree.GetItemData(on_item)
            self.on_clipboard_path = on_item_path

        else:
            self.send_to_logic(text, path)

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

            path = os.path.join(father_path, element)
            if element == self.my_ip:
                element = 'my_pc'

            new_item = self.tree.AppendItem(father, element, data=path)

            print('first:', self.tree.GetItemData(self.tree.GetFirstVisibleItem()))
            self.path_item[path] = new_item
            self.add_pic(new_item, element, folder)
            if folder:
                self.folders.append(path)
                self.convert_to_tree(dic, new_item)


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
            self.send_to_logic('open', path)


    @staticmethod
    def show_error(error: str):
        """
        gets error and tells it to user
        :param error: the error explanation
        """
        wx.MessageBox(error, "Error", wx.OK | wx.ICON_ERROR)




if __name__ == '__main__':
    app = wx.App(False)
    first = TreeFrame(None, Queue())
    app.MainLoop()
