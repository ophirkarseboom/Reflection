import queue
import threading
import time

from Reflection.settings import Settings
from Reflection.comms.client_comm import ClientComm
from Reflection.protocols import general_client_protocol as client_protocol
from Reflection.protocols import server_protocol
import os
from Reflection.local_handler.file_handler import FileHandler
from Reflection.comms.server_comm import ServerComm




def rcv_comm(comm, q):
    """
    gets data from server or clients and calls functions accordingly
    :param comm: client or server comm
    :param q: msg q
    """
    commands = {'23': handle_delete, '16': handle_open_file, '21': handle_rename, '31': handle_asked_file_tree, '32': handle_create, '34': handle_status_mac, }
    while True:
        is_server = isinstance(comm, ServerComm)
        if is_server:
            ip, data = q.get()
            if data == 'close':
                continue
            data = server_protocol.unpack(data)

        else:
            ip = None
            data = client_protocol.unpack(q.get())
        if not data:
            print('got None from protocol')
            continue

        print('data got:', data)

        opcode, params = data
        if is_server:
            commands[opcode](ip, comm, params)
        else:
            commands[opcode](comm, params)


def handle_open_file(got_ip: str, server: ServerComm, vars: list):
    """
    getting server comm and path of file to open and sends its data
    :param server: server comm
    :param vars: path
    :return: None
    """
    if len(vars) != 1:
        print('error in opening file')
        return

    print('ok great')
    path = vars[0]
    user = FileHandler.get_user(path)
    local_path = FileHandler.remove_ip(user, path)
    if os.path.isfile(local_path):
        with open(local_path, 'rb') as f:
            file = f.read()

        print('path:', path)
        server.send_file(got_ip, path, file)

        # server.send(got_ip, client_protocol.pack_status_open_file(True, path))
        # server.send(got_ip, file)

    else:
        server.send(got_ip, client_protocol.pack_status_open_file(False))

def handle_create(client: ClientComm, vars: list):
    """
    creates what server sent if possible and returns status
    :param client: client comm
    :param vars: location of creation and it's type
    :return: None
    """
    location, typ = vars
    status = FileHandler.create(location, typ)
    client.send(client_protocol.pack_status_create(status, location, typ))

def handle_rename(client: ClientComm, vars: list):
    """
    renames a file\folder
    :param client: client comm
    :param vars: location of object to rename and the new name
    :return: None
    """
    location, new_name = vars
    status = FileHandler.rename(location, new_name)
    client.send(client_protocol.pack_status_rename(status, location, new_name))


def handle_delete(client: ClientComm, vars: list):
    """
    deletes what server sent if possible and returns status to server
    :param client: client comm
    :param vars: location to delete
    :return: None
    """
    location = vars[0]
    status = FileHandler.delete(location)
    client.send(client_protocol.pack_status_delete(status, location))


def send_mac():
    """
    sends the mac to server
    """
    to_send = client_protocol.pack_mac(Settings.get_mac_address())
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
    print('got to handle_asked_file_tree')
    folder = vars[0]
    folder_path = f'{FileHandler.root}{folder}'
    print(folder_path)
    time.sleep(1)
    print('folder_path:', folder_path)
    if os.path.isdir(folder_path):

        client.send(client_protocol.pack_file_tree(folder_path))


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
