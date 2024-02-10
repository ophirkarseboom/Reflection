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




def rcv_comm(comm, q):
    """
    gets data from server and calls functions accordingly
    :param : client comm
    """
    commands = {'34': handle_status_mac, '31': handle_asked_file_tree}
    while True:
        data = protocol.unpack(q.get())
        if not data:
            print('got None from protocol')
            continue

        print('data from server:', data)
        opcode, params = data
        commands[opcode](comm, params)


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
    server_ip = Settings.server_ip
    port = 2000
    client = ClientComm(server_ip, port, client_rcv_q, 6, 'G')

    threading.Thread(target=rcv_comm, args=(client, client_rcv_q,), daemon=True).start()
    send_mac()
    while True:
        pass
