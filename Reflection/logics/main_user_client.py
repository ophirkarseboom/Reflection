from queue import Queue
import threading

from Reflection.comms import client_comm
from Reflection.protocols import user_client_protocol as protocol
from uuid import getnode
from collections import deque
import os
from Reflection.file_stuff.file_handler import FileHandler
from Reflection.settings import Settings
import time
import netifaces as ni


class MainUserClient:

    def __init__(self):
        self.folders = {}
        self.server_rcv_q = Queue()
        self.client = client_comm.ClientComm(Settings.server_ip, Settings.server_port, self.server_rcv_q, 6, 'U')
        self.user_name = 'imri1'
        self.file_handler = FileHandler(self.user_name)
        self.handle_tree = Queue()

        threading.Thread(target=self.rcv_comm, args=(self.server_rcv_q,), daemon=True).start()
        self.do_register('12345')
        self.do_connect('12345')



    def rcv_comm(self, q):
        """
        gets data from server and calls functions accordingly
        :param : client comm
        """

        commands = {'02': self.handle_status_register, '04': self.handle_status_login, '05': self.handle_got_file_tree}
        while True:
            data = protocol.unpack(q.get())
            if not data:
                print('got None from protocol')
                continue

            print('data from server:', data)
            opcode, params = data


            commands[opcode](params)


    def navigate_folders(self):
        """
        gets file tree and lets user navigate through it
        :return: None
        """

        last_dir = deque()
        self.folders = {self.file_handler.user_path: [',']}
        cwd = self.file_handler.user_path
        while True:

            # combine new tree
            while not self.handle_tree.empty():
                new_folders = self.handle_tree.get()


                self.folders.update(new_folders)

                ip_path = list(new_folders.keys())[0]
                ip = os.path.basename(ip_path)
                self.folders[self.file_handler.user_path].insert(0, ip)



            print(self.folders)
            print_directory(cwd, self.folders)
            print()
            print_nice('enter something to do: ', 'blue')
            to_do = input().split()
            command = to_do[0]
            param = None

            if len(to_do) > 1:
                param = to_do[1]

            path = cwd
            if not cwd.endswith('\\'):
                path += '\\'

            if command == 'exit':
                break
            elif command == 'in':
                path += param
                if path in self.folders.keys():
                    last_dir.append(cwd)
                    cwd = path
            elif command == 'back':
                if len(last_dir) == 0:
                    print_nice("this is root directory, you can't got back", 'red')
                    print()
                else:
                    cwd = last_dir.pop()

            elif command == 'create':
                path += param
                print(self.file_handler.is_local(path))


            else:
                print_nice('wrong input try again', 'red')
                print()


    def create(self, path, typ, name):
        """
        gets path and typ, creates it
        :param path: path of object to create
        :param typ: type of object
        :param name: name of object
        :return: None
        """
        if self.file_handler.is_local(path):
            pass
            # create local and add
        else:
            pass
            # ask server to add and add




    def handle_status_register(self, vars):
        """
        gets status and shows user what happened
        :param vars: success or failure
        :return: None
        """
        success = vars[0]
        if success == 'ok':
            print('registered')
        else:
            print('could not register')


    def handle_status_login(self, vars):
        """
        gets status, shows user what happened also creates hidden root directory if success and starts navigate folder
        :param vars: success or failure
        :return: None
        """
        success = vars[0]
        if success == 'ok':
            print('you are signed in')
            self.file_handler.create_root()
            thread_handle_tree = threading.Thread(target=self.navigate_folders, daemon=True)
            thread_handle_tree.start()

        else:
            print('could not sign in')


    def handle_got_file_tree(self, vars):
        """
        gets file tree and start interaction with user about files
        :param vars: file tree
        :return: None
        """
        self.handle_tree.put(vars[0])
        # need to do grpahic stuff




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


def print_nice(text, color):
    bold = '1m'
    red = '91m'
    yellow = '93m'
    blue = '94m'
    if color == 'red':
        color = red
    elif color == 'bold':
        color = bold
    elif color == 'yellow':
        color = yellow
    elif color == 'blue':
        color = blue
    else:
        color = '0m'

    bold_text = f"\033[{color}" + text + "\033[0m"
    print(bold_text, end='\t')


def print_directory(fold, folders):
    print_nice(fold, 'yellow')
    print()
    bold = True
    count = 0
    for obj in folders[fold]:
        if obj == ',':
            bold = False
        else:
            obj = "{:<40}".format(obj)
            count += 1
            if bold:
                print_nice(obj, 'bold')
            else:
                print(obj, end='\t')
            if count == 4:
                print()
                count = 0


def get_mac_address():
    """ returns  mac address"""
    return ':'.join(['{:02x}'.format((getnode() >> i) & 0xff) for i in range(0, 8 * 6, 8)][::-1])

if __name__ == '__main__':

    MainUserClient()
    while True:
        pass