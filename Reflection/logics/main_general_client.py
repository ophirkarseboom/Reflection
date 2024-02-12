import queue
import threading
import time

from Reflection.settings import Settings
from Reflection.comms.client_comm import ClientComm
from Reflection.protocols import general_client_protocol as protocol
from uuid import getnode
import sys
import os
from Reflection.file_stuff.file_handler import FileHandler
import netifaces as ni
from Reflection.comms.server_comm import ServerComm




def rcv_comm(comm, q):
    """
    gets data from server and calls functions accordingly
    :param : client comm
    """
    commands = { '31': handle_asked_file_tree, '32': handle_create, '34': handle_status_mac}
    while True:
        data = protocol.unpack(q.get())
        if not data:
            print('got None from protocol')
            continue

        print('data from server:', data)
        opcode, params = data
        commands[opcode](comm, params)


def handle_create(client: ClientComm, vars: list):
    """
    creates what server sent if possible and returns status
    :param client: client comm
    :param vars: location of creation and it's type
    :return: None
    """
    location, typ = vars
    status = FileHandler.create(location, typ)
    client.send(protocol.pack_status_create(status, location, typ))


def send_mac():
    """
    sends the mac to server
    """
    to_send = protocol.pack_mac(Settings.get_mac_address())
    client.send(to_send)


def handle_status_mac(client: ClientComm, vars: list):
    """
    gets status and shows user what happened
    :param vars: success or failure
    :return: None
    """
    success = vars[0]
    if success == 'ok':
        print('sent mac successfully')
    else:
        print("a user didn't login through this computer")


def handle_asked_file_tree(client: ClientComm, vars: list):
    """
    gets folder and sends server file tree of folder
    :param client: the comm got
    :param vars: folder name
    :return: None
    """

    folder = vars[0]
    folder_path = f'{FileHandler.root}{folder}'
    print(folder_path)
    time.sleep(1)
    if os.path.isdir(folder_path):
        print('nice')
        client.send(protocol.pack_file_tree(folder_path))


if __name__ == '__main__':
    client_rcv_q = queue.Queue()
    server_rcv_q = queue.Queue()
    server_ip = Settings.server_ip
    port = 2000
    client = ClientComm(server_ip, port, client_rcv_q, 6, 'G')
    file_server = ServerComm(Settings.pear_port, server_rcv_q, 8)
    
    threading.Thread(target=rcv_comm, args=(client, client_rcv_q,), daemon=True).start()
    threading.Thread(target=rcv_comm, args=(file_server, server_rcv_q,), daemon=True).start()

    # sending main server client's mac
    send_mac()

    while True:
        pass
