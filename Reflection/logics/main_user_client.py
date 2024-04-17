from queue import Queue
import threading
import Reflection.protocols.general_client_protocol as general_client_protocol
from Reflection.comms.client_comm import ClientComm
from Reflection.protocols import user_client_protocol as protocol
from uuid import getnode
import os
from Reflection.local_handler.file_handler import FileHandler
from Reflection.local_handler import process_handler
from Reflection.settings import Settings
import wx
from pubsub import pub
from Reflection.graphics.graphics import MyFrame
import win32file


class MainUserClient:

    def __init__(self):
        self.folders = {}

        self.server_rcv_q = Queue()
        self.client = ClientComm(Settings.server_ip, Settings.server_port, self.server_rcv_q, 6, 'U')
        self.user_name = ''
        self.handle_tree = Queue()
        self.ip_comm = {}
        self.graphic_q = Queue()
        self.downloads = {}  # {local path, path on gui}

        threading.Thread(target=self.rcv_comm, args=(self.server_rcv_q,), daemon=True).start()
        threading.Thread(target=self.rcv_graphic, args=(self.graphic_q,), daemon=True).start()
        app = wx.App(False)
        self.frame = MyFrame(self.graphic_q)
        self.frame.Show()
        app.MainLoop()

    def monitor_file(self, file_path: str):
        """
        monitors a file and sends server what changed in file
        :param file_path: path for file to monitor
        :return: None
        """
        modified = 0x00000003
        FILE_LIST_DIRECTORY = 0x0001
        FILE_NOTIFY_CHANGE_FILE_NAME = 0x0001
        FILE_NOTIFY_CHANGE_LAST_WRITE = 0x0010
        FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
        OPEN_EXISTING = 3

        path_to_watch, file_name = FileHandler.split_path_last_part(file_path)
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
            # changed = False
            while True:
                try:
                    result = win32file.ReadDirectoryChangesW(
                        directory_handle,
                        4096,
                        True,  # Watch subtree
                        FILE_NOTIFY_CHANGE_LAST_WRITE | FILE_NOTIFY_CHANGE_FILE_NAME,
                        None
                    )

                    for action, name_monitored in result:

                        if action == modified and name_monitored == file_name:
                            print('saved file in monitor')
                            to_send_path = file_path.replace(Settings.local_path_directory, '', 1)
                            self.save_file(file_path, to_send_path)

                except Exception:
                    break

    def save_file(self, from_path, to_path):
        """
        sends file data to ip inside path, if local saves path local
        :param from_path: location of data to send
        :param to_path: the path for client to save data in
        :return: None
        """
        if not os.path.isfile(from_path):
            self.call_error('could not save file data')
            return

        # get file data
        with open(from_path, 'rb') as f:
            file_data = f.read()

        if self.file_handler.is_local(to_path):
            to_path = self.file_handler.remove_ip(self.user_name, to_path)
            with open(to_path, 'wb') as f:
                f.write(file_data)

        # need to send to other computer
        else:
            ip_to_send = FileHandler.extract_ip(self.user_name, to_path)
            if ip_to_send in self.ip_comm:
                comm = self.ip_comm[ip_to_send]
            else:
                rcv_q = Queue()
                comm = ClientComm(ip_to_send, Settings.pear_port, rcv_q, 8)
                self.ip_comm[ip_to_send] = comm
                threading.Thread(target=self.rcv_comm, args=(rcv_q,), daemon=True).start()

            header = protocol.pack_change_file(to_path)
            comm.send_file(header, file_data)

    def visualize_open_file(self, file_path):
        """
        opening file to user and activates monitoring on file
        :param file_path: path of file
        :return: None
        """
        # start monitoring file
        threading.Thread(target=self.monitor_file, args=(file_path,), daemon=True).start()

        process_name = process_handler.get_process_name(file_path)
        ls1 = process_handler.get_all_pid(process_name)
        dir_path, _ = FileHandler.split_path_last_part(file_path)
        FileHandler.open_file(file_path)

        # wait for file to be added to pid list
        while True:
            ls2 = process_handler.get_all_pid(process_name)
            if ls2 != ls1:
                break

        new_pid = set(ls2) - set(ls1)
        pid = list(new_pid)[0]

        process_handler.wait_for_process_to_close(pid)

        FileHandler.delete(file_path)
        print('ended visualize file')

    def rcv_graphic(self, q: Queue):
        """
        gets q from graphics and handles what got
        :param q: q gets from graphic
        :return: None
        """
        while True:
            print(self.folders)
            command, param_got = q.get()
            print('command:', command, '       param:', param_got)
            if command == 'create file':
                path, name = self.file_handler.split_path_last_part(param_got)
                name = name.split('.')
                typ = name[-1]
                name = ''.join(name[:-1])
                self.create(path, name, typ)
            elif command == 'create folder':
                path, name = self.file_handler.split_path_last_part(param_got)
                self.create(path, name, 'fld')

            elif command == 'open':
                self.get_file_data(param_got)

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
                if param_got.count(',') != 1:
                    self.call_error('problem with password or username')
                    continue
                self.user_name, password = param_got.split(',')
                print('self.username:', self.user_name)
                self.do_register(password)

            elif command == 'upload file':
                if param_got.count(',') != 1:
                    self.call_error('problem with uploading file')
                    continue
                dir_path, from_path = param_got.split(',')
                name = os.path.basename(from_path)
                to_path = f'{dir_path}\\{name}'
                name, typ = FileHandler.split_name_typ(name)

                self.handle_status_create(['ok', f'{dir_path}\\{name}', typ])
                self.save_file(from_path, to_path)

            elif command == 'download':
                if param_got.count(',') != 1:
                    self.call_error('problem with uploading file')
                    continue
                downloaded, download_to = param_got.split(',')

                print('download:', downloaded)
                dir_path, name = FileHandler.split_path_last_part(download_to)
                typ = os.path.basename(downloaded).split('.')[-1]
                FileHandler.create(f'{dir_path}\\{name}', str(typ))
                if '.' not in os.path.basename(download_to):
                    download_to += f'.{typ}'
                self.downloads[download_to] = downloaded
                print('local path:', download_to)
                self.get_file_data(downloaded)

            elif command == 'paste':
                if param_got.count(',') != 1:
                    self.call_error('problem with uploading file')
                    continue
                file_to_copy, copy_to = param_got.split(',')
                self.clone(file_to_copy, copy_to)

            elif command == 'move':
                if param_got.count(',') != 1:
                    self.call_error('problem with uploading file')
                    continue
                file_to_move, move_to = param_got.split(',')
                self.move_file(file_to_move, move_to)

            else:
                print('wrong output')


    def move_file(self, file_to_move: str, move_to: str):
        """
        moves file from one folder to another
        :param file_to_move: full path of the file to move
        :param move_to: the path to move the file to
        :return: None
        """
        # if got a file path changing it to the folder
        if move_to not in self.folders:
            move_to, _ = FileHandler.split_path_last_part(move_to)

        ip_from = FileHandler.extract_ip(self.user_name, file_to_move)
        ip_to = FileHandler.extract_ip(self.user_name, move_to)

        print('move_to:', move_to)
        print('file_to_move:', file_to_move)

        file_dir_path, file_name = FileHandler.split_path_last_part(file_to_move)
        file_name = FileHandler.build_name_for_file(self.folders, move_to, file_to_move, '(moved)')
        new_file_path = str(os.path.join(move_to, file_name))
        # if moving to same dir
        if move_to == file_dir_path:
            return

        if self.file_handler.is_local(move_to) and self.file_handler.is_local(file_to_move):
            # making folders local
            local_new_file_path = FileHandler.remove_ip(self.user_name, new_file_path)
            local_file_to_move = FileHandler.remove_ip(self.user_name, file_to_move)

            moved = FileHandler.move(local_file_to_move, local_new_file_path)
            if moved:
                print('removing:', file_to_move)
                self.folders_remove(file_to_move)
                print(f'adding: {move_to}\\{file_name}')
                file_name, typ = FileHandler.split_name_typ(file_name)
                # general_client_protocol.pack_status_move(moved, local_file_to_move, f'{local_move_to}\\{file_name}')
                self.folders_add(move_to, file_name, typ)
                self.folders_remove(file_to_move)
            else:
                self.call_error(f'could not move {file_name}')

        else:
            self.client.send(protocol.pack_do_move(file_to_move, new_file_path))


    def clone(self, file_to_copy: str, copy_to: str):
        """
        copies file from one folder to another
        :param file_to_copy: full path of the file to copy
        :param copy_to: the path to copy the file to
        :return: None
        """
        # if got a file path changing it to the folder
        if copy_to not in self.folders:
            copy_to, _ = FileHandler.split_path_last_part(copy_to)

        ip_from = FileHandler.extract_ip(self.user_name, file_to_copy)
        ip_to = FileHandler.extract_ip(self.user_name, copy_to)

        if self.file_handler.is_local(copy_to) and self.file_handler.is_local(file_to_copy):

            # making folders local
            local_copy_to = FileHandler.remove_ip(self.user_name, copy_to)
            local_file_to_copy = FileHandler.remove_ip(self.user_name, file_to_copy)

            file_folder, file_name = FileHandler.split_path_last_part(local_file_to_copy)

            new_file_name = FileHandler.build_name_for_file(local_copy_to, local_file_to_copy, '(copy)')
            print('new_file_name:', new_file_name)
            print('local_copy_to:', local_copy_to)

            copied = FileHandler.direct_copy_file(f'{file_folder}\\{file_name}',
                                                  f'{local_copy_to}\\{new_file_name}')

            if copied:
                file_name, typ = FileHandler.split_name_typ(new_file_name)
                self.folders_add(copy_to, file_name, typ)

        elif ip_from == ip_to:
            self.client.send(protocol.pack_do_clone(file_to_copy, copy_to))

        else:
            self.call_error('cannot copy from 2 different computers')

    def handle_status_rename(self, vars: list):
        """
        gets status of renaming and shows user what happened
        :param vars: status, location, new_name
        :return: None
        """
        status, location, new_name = vars
        if '.' in new_name:
            just_name, typ = FileHandler.split_name_typ(new_name)
        else:
            typ = 'fld'
            just_name, _ = FileHandler.split_name_typ(new_name)
        # do local stuff of creating file
        if status == 'ok':
            self.folders_remove(location)
            folder_path, _ = self.file_handler.split_path_last_part(location)
            self.folders_add(folder_path, just_name, typ)
        else:
            self.call_error(f'could not rename to "{new_name}"')


    def handle_status_clone(self, vars: list):
        """
        gets status of cloning and shows user what happened
        :param vars: status, old_location, new_location
        :return: None
        """
        status, copy_from, copy_to = vars
        print('copy_from:', copy_from)
        print('copy_to:', copy_to)
        folder_copied_to, file_name = FileHandler.split_path_last_part(copy_to)

        just_name, typ = FileHandler.split_name_typ(file_name)

        # informing graphics
        if status == 'ok':
            self.folders_add(folder_copied_to, just_name, typ)
        else:
            self.call_error(f'could not clone {just_name}.{typ}')


    def handle_status_move(self, vars: list):
        """
        gets status of moving and shows user what happened
        :param vars: status, old_location, new_location
        :return: None
        """
        status, move_from, move_to = vars
        folder_copied_to, file_name = FileHandler.split_path_last_part(move_to)

        just_name, typ = FileHandler.split_name_typ(file_name)

        # informing graphics
        if status == 'ok':
            self.folders_add(folder_copied_to, just_name, typ)
            self.folders_remove(move_from)
        else:
            self.call_error(f'could not clone {just_name}.{typ}')

    def rename(self, path: str, new_name: str):
        """
        gets path and typ, creates it
        :param path: path of object to create
        :param new_name: the new name of the file
        :return: None
        """
        # trying to change computers folder
        if path in self.folders and '.' in os.path.basename(path):
            self.call_error('cannot rename computers directory')
            return

        if self.file_handler.is_local(path):
            local = self.file_handler.remove_ip(self.user_name, path)
            if '.' in new_name:
                just_name, typ = FileHandler.split_name_typ(new_name)
            else:
                typ = 'fld'
                just_name, _ = FileHandler.split_name_typ(new_name)

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
                    '09': self.handle_status_rename, '07': self.handle_status_create, '13': self.handle_status_move,
                    '15': self.handle_status_clone, '17': self.handle_status_open, '11': self.handle_status_delete,
                    '19': self.handle_status_saved_file}
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

        while True:
            new_folders = {}
            # gets new folder adds it to folders dict
            folders_got = self.handle_tree.get()
            new_folders[user_path] = [',']
            self.folders.update(folders_got)

            # gets ip of computer got from
            ip_path = list(folders_got.keys())[0]
            ip = os.path.basename(ip_path)

            # adds ip to folders in path needed
            self.folders[user_path].insert(0, ip)
            new_folders.update(folders_got)
            new_folders[user_path].insert(0, ip)
            wx.CallAfter(pub.sendMessage, "update_tree", dic=new_folders)


    def handle_status_saved_file(self, vars: list):
        """
        calling error if was a problem saving file
        :param vars: status and path
        :return: None
        """
        status = (vars[0] == 'ok')
        if len(vars) != 2:
            self.call_error(f"couldn't save file, problem communicating with other pc")
            return
        path = vars[1]
        if not status:
            self.call_error(f"couldn't save file: {path}")

    def handle_status_open(self, vars: list):
        """
        showing user the file if opened
        :param vars: status and path
        :return: None
        """
        status = vars[0]
        if status:

            path = vars[1]
            print('path:', path)
            download_path = path.replace(Settings.local_path_directory, '', 1)
            print('downloaded_path:', download_path)
            print('downloads:', self.downloads)

            if download_path in self.downloads.values():
                local_path = next(filter(lambda item: item[1] == download_path, self.downloads.items()), None)[0]
                FileHandler.direct_copy_file(path, local_path)
                del self.downloads[local_path]

            elif os.path.isfile(path):

                threading.Thread(target=self.visualize_open_file, args=(path,), daemon=True).start()
            else:
                print('error in opening file')
        else:
            self.call_error("couldn't open file")

    def get_file_data(self, path: str):
        """
        gets path of file with its name and opens it
        :param path: path of file
        return:
        """

        # file is local so opens it immediately
        if self.file_handler.is_local(path):
            local = self.file_handler.remove_ip(self.user_name, path)
            FileHandler.open_file(local)

        # if user asked to download local file
        elif path in self.downloads and os.path.isfile(FileHandler.remove_ip(self.user_name, self.downloads[path])):
            download_from_path = FileHandler.remove_ip(self.user_name, self.downloads[path])
            print('download from:', download_from_path)
            print('download to:', path)
            FileHandler.direct_copy_file(download_from_path, path)
            del self.downloads[path]

        # if file is on another computer
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
        print(self.folders)
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
            print('user_path:', user_path)

            # thread that waits for getting file trees
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
