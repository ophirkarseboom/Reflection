from queue import Queue
import threading

from Reflection.comms.client_comm import ClientComm
from Reflection.protocols import user_client_protocol as protocol
from uuid import getnode
from collections import deque
import os
from Reflection.file_stuff.file_handler import FileHandler
from Reflection.settings import Settings
import wx
from pubsub import pub
import time
from Reflection.graphics.graphics import MyFrame
import win32file


class MainUserClient:

    def __init__(self):
        self.folders = {}

        self.server_rcv_q = Queue()
        self.client = ClientComm(Settings.server_ip, Settings.server_port, self.server_rcv_q, 6, 'U')
        self.user_name = ''
        self.handle_tree = Queue()
        self.ip_comm = {str: ClientComm}

        self.graphic_q = Queue()

        threading.Thread(target=self.rcv_comm, args=(self.server_rcv_q,), daemon=True).start()
        threading.Thread(target=self.rcv_graphic, args=(self.graphic_q,), daemon=True).start()
        self.monitor_thread = threading.Thread(target=self.monitor_files, daemon=True)
        app = wx.App(False)
        self.frame = MyFrame(self.graphic_q)
        self.frame.Show()
        app.MainLoop()


    def monitor_files(self):
        """

        :return:
        """
        FILE_LIST_DIRECTORY = 0x0001
        FILE_NOTIFY_CHANGE_FILE_NAME = 0x0001
        FILE_NOTIFY_CHANGE_DIR_NAME = 0x0002
        FILE_NOTIFY_CHANGE_LAST_WRITE = 0x0010
        FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
        OPEN_EXISTING = 3

        path_to_watch = Settings.local_changes_path + self.user_name

        file_actions = {
            0x00000001:
                "Added",
            0x00000002:
                "Removed",
            0x00000003:
                "Modified",
            0x00000004:
                "Renamed old name",
            0x00000005:
                "Renamed new name"
        }

        directory_handle = win32file.CreateFileW(
            path_to_watch,
            FILE_LIST_DIRECTORY,  # No access (required for directories)
            win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE | win32file.FILE_SHARE_DELETE,
            None,
            OPEN_EXISTING,
            FILE_FLAG_BACKUP_SEMANTICS,
            None
        )
        if directory_handle == -1:
            print("Error opening directory")
        else:
            while True:
                try:
                    result = win32file.ReadDirectoryChangesW(
                        directory_handle,
                        4096,
                        True,  # Watch subtree
                        FILE_NOTIFY_CHANGE_LAST_WRITE | FILE_NOTIFY_CHANGE_FILE_NAME,
                        None
                    )

                    for action in result:
                        if file_actions[action[0]] == "Modified" and not action[1].startswith('~'):
                            print('yesssssssssssssssssssssssssssssssssssssssssssss')
                except Exception as e:
                    break


    def rcv_graphic(self, q: Queue):
        """
        gets q from graphics and handles what got
        :param q: q gets from graphic
        :return: None
        """
        while True:
            print(self.folders)
            command, param_got = q.get()
            print('command:', command)
            if command == 'create file':
                path, name = self.file_handler.split_path_last_part(param_got)
                print('path:', path)
                name = name.split('.')
                typ = name[-1]
                name = ''.join(name[:-1])
                print('name:', name)
                print('typ:', typ)
                self.create(path, name, typ)
            elif command == 'create folder':
                path, name = self.file_handler.split_path_last_part(param_got)
                self.create(path, name, 'fld')

            elif command == 'open':
                self.open(param_got)

            elif command == 'delete':
                self.delete(param_got)

            elif command == 'rename':
                path, new_name = self.file_handler.split_path_last_part(param_got)
                print('path:', path)
                print('new name:', new_name)
                self.rename(path, new_name)

            elif command == 'login':
                if param_got.count(',') != 1:
                    self.call_error('problem with password or username')
                    continue
                self.user_name, password = param_got.split(',')
                print('self.username:', self.user_name)
                self.do_connect(password)

            elif command == 'register':
                if param_got.count(',') != 1 or '\\' in param_got:
                    self.call_error('problem with password or username')
                    continue
                self.user_name, password = param_got.split(',')
                print('self.username:', self.user_name)
                self.do_register(password)

            else:
                print()

    def handle_status_rename(self, vars: list):
        """
        gets status of renaming and shows user what happened
        :param vars: status, location, new_name
        :return: None
        """
        status, location, new_name = vars
        if '.' in new_name:
            just_name, typ = new_name.split('.')
        else:
            typ = 'fld'
            just_name = new_name.split('.')[0]
        # do local stuff of creating file
        if status == 'ok':
            self.folders_remove(location)
            folder_path, _ = self.file_handler.split_path_last_part(location)
            self.folders_add(folder_path, just_name, typ)
        else:
            self.call_error(f'could not rename to "{new_name}"')

    def rename(self, path: str, new_name: str):
        """
        gets path and typ, creates it
        :param path: path of object to create
        :return: None
        """
        # trying to change computers folder
        if path in self.folders and '.' in os.path.basename(path):
            self.call_error('cannot rename computers directory')
            return

        if self.file_handler.is_local(path):
            local = self.file_handler.remove_ip(self.user_name, path)
            if '.' in new_name:
                just_name, typ = new_name.split('.')
            else:
                typ = 'fld'
                just_name = new_name.split('.')[0]
            # do local stuff of creating file
            if self.file_handler.rename(local, new_name):

                self.folders_remove(path)
                folder_path, _ = self.file_handler.split_path_last_part(path)
                self.folders_add(folder_path, just_name, typ)
            else:
                self.call_error(f'could not rename to "{new_name}"')
        else:
            self.client.send(protocol.pack_do_rename(path, new_name))


    def call_error(self, error: str):
        """
        gets error and sends it to graphic
        :param error: error to show user
        """
        wx.CallAfter(pub.sendMessage, "error", error=error)

    def delete(self, path: str):
        """
        gets path of file with its name and deletes it
        :param path: path of file
        return: None
        """
        # trying to change computers folder
        if path in self.folders and '.' in os.path.basename(path):
            self.call_error('cannot delete computers directory')
            return

        if self.file_handler.is_local(path):
            local = self.file_handler.remove_ip(self.user_name, path)

            # do local stuff deleting file
            self.file_handler.delete(local)
            self.folders_remove(path)
        else:
            self.client.send(protocol.pack_do_delete(path))

    def rcv_comm(self, q):
        """
        gets data from server and calls functions accordingly
        :param : client comm
        """

        commands = {'02': self.handle_status_register, '04': self.handle_status_login, '05': self.handle_got_file_tree,
                    '09': self.handle_status_rename, '07': self.handle_status_create, '17': self.handle_status_open, '11': self.handle_status_delete}
        while True:
            data = protocol.unpack(q.get())
            if not data:
                print('got None from protocol')
                continue

            print('data from server:', data)
            opcode, params = data

            commands[opcode](params)

    def get_file_tree(self):
        """
        gets file tree and lets user navigate through it
        :return: None
        """
        print('user_path:', self.file_handler.user_path)
        user_path = self.file_handler.user_path[:-1]
        new_folders = {}
        while True:
            # gets new folder adds it to folders dict
            folders_got = self.handle_tree.get()
            print('folders_got:', folders_got)
            new_folders[user_path] = [',']
            self.folders.update(folders_got)

            # gets ip of computer got from
            ip_path = list(folders_got.keys())[0]
            ip = os.path.basename(ip_path)

            # adds ip to folders in path needed
            self.folders[user_path].insert(0, ip)
            new_folders.update(folders_got)
            new_folders[user_path].insert(0, ip)
            print('new_folders:', new_folders)
            wx.CallAfter(pub.sendMessage, "update_tree", dic=new_folders)


    def handle_status_open(self, vars: list):
        """
        showing user the file if opened
        :param vars: status and path
        :return: None
        """
        status = vars[0]
        if status:

            path = vars[1]
            if os.path.isfile(path):
                FileHandler.open_file(path)

                # starting monitoring
                if not self.monitor_thread.is_alive():
                    self.monitor_thread.start()
            else:
                print('error in opening file')
        else:
            print("couldn't open file at general_client")

    def open(self, path: str):
        """
        gets path of file with its name and opens it
        :param path: path of file
        return:
        """

        if self.file_handler.is_local(path):
            local = self.file_handler.remove_ip(self.user_name, path)
            os.system('start "" "' + local + '"')
        else:

            ip_to_connect = self.file_handler.extract_ip(self.user_name, path)
            # setting up pear to pear
            if ip_to_connect not in self.ip_comm:
                rcv_q = Queue()

                comm = ClientComm(ip_to_connect, Settings.pear_port, rcv_q, 8)
                self.ip_comm[ip_to_connect] = comm
                threading.Thread(target=self.rcv_comm, args=(rcv_q,), daemon=True).start()

            else:
                comm = self.ip_comm[ip_to_connect]

            comm.send(protocol.pack_do_open_file(path))

    def folders_remove(self, path):
        """
        gets path and removes it from folders and tells graphic
        :param path: path to delete
        """
        father_path, name = self.file_handler.split_path_last_part(path)
        if path in self.folders:
            del self.folders[path]

        if father_path in self.folders and name in self.folders[father_path]:
            self.folders[father_path].remove(name)

        wx.CallAfter(pub.sendMessage, "delete", path=path)

    def folders_add(self, path, name, typ):
        """
        gets path and adds it to folders dict
        :param path: path of father
        :param name: name of file
        :param typ: type of file/folder
        """
        if path.endswith('\\'):
            path = path[:-1]
        if typ == 'fld':
            self.folders[f'{path}\\{name}'] = [',']
            self.folders[path].insert(0, name)

        else:
            self.folders[path].append(f'{name}.{typ}')

        wx.CallAfter(pub.sendMessage, "create", path=path, name=name, typ=typ)

    def create(self, path: str, name: str, typ: str):
        """
        gets path and typ, creates it
        :param path: path of object to create
        :param typ: type of object
        :param name: name of object
        :return: None
        """
        if not path.endswith('\\'):
            path += '\\'
        if self.file_handler.is_local(path):
            local = self.file_handler.remove_ip(self.user_name, path)
            local = local + name

            # do local stuff of creating file
            self.file_handler.create(local, typ)
            self.folders_add(path, name, typ)
        else:
            self.client.send(protocol.pack_do_create(path + name, typ))

    def handle_status_create(self, vars: list):
        """
        gets status of creation and shows user what happened
        :param vars: status, location, type
        :return: None
        """
        status, location, typ = vars
        if status == 'ok':
            path, name = FileHandler.split_path_last_part(location)
            self.folders_add(path, name, typ)

        else:
            print('could not create')

    def handle_status_delete(self, vars: list):
        """
        gets status of creation and shows user what happened
        :param vars: status, location, type
        :return: None
        """
        status, location = vars
        if status == 'ok':
            self.folders_remove(location)

        else:
            print('could not register')

    def handle_status_register(self, vars):
        """
        gets status and shows user what happened
        :param vars: success or failure
        :return: None
        """
        success = vars[0]
        if success == 'ok':
            wx.CallAfter(pub.sendMessage, 'notification', notification='great you can now login with this name and '
                                                                       'password')
            print('registered')
        else:
            self.call_error('username already exists')


    def handle_status_login(self, vars):
        """
        gets status, shows user what happened also creates hidden root directory if success and starts navigate folder
        :param vars: success or failure
        :return: None
        """
        success = vars[0]
        if success == 'ok':
            print('you are signed in')
            self.file_handler = FileHandler(self.user_name)
            user_path = self.file_handler.user_path[:-1]
            self.folders = {user_path: [',']}
            self.file_handler.create_root()
            threading.Thread(target=self.get_file_tree, daemon=True).start()

            # grpahic
            wx.CallAfter(pub.sendMessage, 'login')

        else:
            self.call_error('username or password does not exist')
            print('could not sign in')

    def handle_got_file_tree(self, vars):
        """
        gets file tree and start interaction with user about files
        :param vars: file tree
        :return: None
        """
        self.handle_tree.put(vars[0])

    def do_register(self, password):
        """
        gets username and password and sends it to server by protocol to register
        :param password: password
        :return: None
        """
        to_send = protocol.pack_register(self.user_name, password)
        self.client.send(to_send)

    def do_connect(self, password):
        """
        gets username and password and sends it to server by protocol to sign in
        :param password: password
        :return: None
        """
        to_send = protocol.pack_sign_in(self.user_name, password, get_mac_address())
        self.client.send(to_send)



def get_mac_address():
    """ returns  mac address"""
    return ':'.join(['{:02x}'.format((getnode() >> i) & 0xff) for i in range(0, 8 * 6, 8)][::-1])


if __name__ == '__main__':
    MainUserClient()