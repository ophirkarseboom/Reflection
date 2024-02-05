from queue import Queue
import threading

from Reflection.comms import client_comm
from Reflection.protocols import user_client_protocol as protocol
from uuid import getnode
from collections import deque
import os
from Reflection.file_stuff.file_handler import FileHandler
import socket
from Reflection.settings import Settings

class MainUserClient:

    def __init__(self):

        self.server_rcv_q = Queue()
        self.my_ip = socket.gethostbyname(socket.gethostname())
        self.client = client_comm.ClientComm(Settings.server_ip, Settings.server_port, self.server_rcv_q, 6, 'U')
        self.user_name = 'ophir'
        threading.Thread(target=rcv_comm, args=(self.server_rcv_q,), daemon=True).start()
        do_connect(self.user_name, '12345')

def print_nice(text, color):
    bold = '1m'
    red = '91m'
    blue = '94m'
    if color == 'red':
        color = red
    elif color == 'bold':
        color = bold
    elif color == 'blue':
        color = blue
    else:
        color = '0m'
    bold_text = f"\033[{color}" + text + "\033[0m"
    print(bold_text, end='\t')


def print_directory(fold, folders):
    print_nice(fold, 'red')
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


def rcv_comm(q):
    """
    gets data from server and calls functions accordingly
    :param : client comm
    """
    # tmp
    handle_tree = Queue()
    thread_handle_tree = None
    commands = {'02': handle_status_register, '04': handle_status_login, '05': handle_got_file_tree}
    while True:

        data = protocol.unpack(q.get())
        if not data:
            print('got None from protocol')
            continue

        print('data from server:', data)
        opcode, params = data
        # temporary
        if opcode == '05':
            handle_tree.put(params)
            if not thread_handle_tree:
                file_handler = FileHandler()

                thread_handle_tree = threading.Thread(target=navigate_folders, args=(params ,handle_tree, file_handler,), daemon=True)
                thread_handle_tree.start()

        else:
            commands[opcode](params)


def navigate_folders(params, get_queue: Queue, file_handler: FileHandler):
    """
    gets file tree and lets user navigate through it
    :param folders: dictionary that represents file tree
    :return: None
    """

    last_dir = deque()
    folders = params[0]
    cwd = list(folders.keys())[0]
    print(folders)
    while True:
        # combine new tree
        if not get_queue.empty():
            new_folders, got_ip = get_queue.get()
            new_folder_key, new_folder_value = next(iter(new_folders.items()))
            old_folder_key, old_folder_value = next(iter(folders.items()))
            if old_folder_key == new_folder_key:
                going_through_folders = True
                for element in old_folder_value:
                    if element == ',':
                        going_through_folders = False

                    elif element in new_folder_value:
                        pass
                    elif going_through_folders:
                        new_folder_value.insert(0, element)
                    else:
                        new_folder_value.append(element)

                folders.update(new_folders)


            else:
                print_nice('something went wrong in adding file tree', 'bold')

        print_directory(cwd, folders)
        print()
        print_nice('enter something to do: ', 'blue')
        to_do = input()



        if cwd.endswith('\\'):
            path = fr'{cwd}{to_do}'
        else:
            path = f'{cwd}\\{to_do}'

        print('path:', path)
        if to_do == 'exit':
            break
        elif path in folders.keys():
            last_dir.append(cwd)
            cwd = path
        elif to_do == 'back':
            if len(last_dir) == 0:
                print_nice("this is root directory, you can't got back", 'red')
                print()
            else:
                cwd = last_dir.pop()

        else:
            print_nice('wrong input try again', 'red')
            print()



def handle_status_register(vars):
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


def handle_status_login(vars):
    """
    gets status and shows user what happened
    :param vars: success or failure
    :return: None
    """
    success = vars[0]
    if success == 'ok':
        print('you are signed in')

    else:
        print('could not sign in')


def handle_got_file_tree(vars):
    """
    gets file tree and start interaction with user about files
    :param vars: file tree
    :return: None
    """
    # need to do grpahic stuff
    pass



def do_register(username, password):
    """
    gets username and password and sends it to server by protocol to register
    :param username: username
    :param password: password
    :return: None
    """
    to_send = protocol.pack_register(username, password)
    client.send(to_send)


def do_connect(username, password):
    """
    gets username and password and sends it to server by protocol to sign in
    :param username: username
    :param password: password
    :return: None
    """
    to_send = protocol.pack_sign_in(username, password, get_mac_address())
    client.send(to_send)


if __name__ == '__main__':

    rcv_q = Queue()
    server_ip = '192.168.56.1'
    my_ip = socket.gethostbyname(socket.gethostname())
    port = 2000
    client = client_comm.ClientComm(server_ip, port, rcv_q, 6, 'U')
    user_name = 'ophir'
    threading.Thread(target=rcv_comm, args=(rcv_q,), daemon=True).start()
    do_connect(user_name, '12345')

    while True:
        pass
