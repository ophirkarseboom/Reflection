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
from queue import Queue





def rcv_comm(comm, q):
    """
    gets data from server or clients and calls functions accordingly
    :param comm: client or server comm
    :param q: msg q
    """
    commands = {'23': handle_delete, '16': handle_open_file, '21': handle_rename, '25': handle_do_move,
                '27': handle_clone, '18': handle_changed_file, '31': handle_asked_file_tree,
                '32': handle_create, '34': handle_status_mac}
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

        # ending thread listening
        if opcode == '00':
            return

        if is_server:
            commands[opcode](ip, comm, params)
        else:
            commands[opcode](comm, params)

def handle_changed_file(got_ip: str, server: ServerComm, vars: list):
    """
    sending status if worked or not to client
    :param server: server comm
    :param vars: status
    :return: None
    """
    if len(vars) != 2:
        print('error while saving file')
        return
    status = (vars[0] == 'ok')
    path = vars[1]
    client_protocol.pack_status_change_file(status, path)

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

    path = vars[0]
    user = FileHandler.get_user(path)
    local_path = FileHandler.remove_ip(user, path)
    if os.path.isfile(local_path):
        with open(local_path, 'rb') as f:
            file = f.read()

        print('path of file to open:', path)
        header = client_protocol.pack_status_open_file(True, path)
        server.send_file(got_ip, header, file)

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


def handle_clone(client: ClientComm, vars: list):
    """
    clones a file
    :param client: client comm
    :param vars: location of object to clone and the new location
    :return: None
    """
    copy_from, copy_to = vars
    print('copy_from:', copy_from)
    print('copy_to:', copy_to)
    new_file_name = FileHandler.build_name_for_file(copy_to, copy_from, '(copy)')
    new_path = str(os.path.join(copy_to, new_file_name))
    status = FileHandler.direct_copy_file(copy_from, new_path)
    client.send(client_protocol.pack_status_clone(status, copy_from, new_path))


def handle_do_move(client: ClientComm, vars: list):
    """
    moves a file
    :param client: client comm
    :param vars: location of object to move and the new location
    :return: None
    """
    move_from, move_to = vars
    username = FileHandler.get_user(move_from)

    move_to_ip = FileHandler.extract_ip(username, move_to)
    my_ip = FileHandler.extract_ip(username, move_from)

    # locally moving file
    if my_ip == move_to_ip:
        local_move_from = FileHandler.remove_ip(username, move_from)
        local_move_to = FileHandler.remove_ip(username, move_to)

        status = FileHandler.move(local_move_from, local_move_to)
        client.send(client_protocol.pack_status_move(status, move_from, move_to))

    # sending file to other computer
    else:
        rcv_q = Queue()

        comm = ClientComm(move_to_ip, Settings.pear_port, rcv_q, 8, 'G')
        ip_comm[move_to_ip] = comm
        threading.Thread(target=rcv_comm, args=(comm, rcv_q), daemon=True).start()
        local_file_data = FileHandler.remove_ip(username, move_from)
        with open(local_file_data, 'rb') as f:
            file_data = f.read()

        header = client_protocol.pack_do_move(move_to, move_from)
        comm.send_file(header, file_data)


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
    ip_comm = {}
    port = 2000
    client = ClientComm(server_ip, port, client_rcv_q, 6, 'G')
    file_server = ServerComm(Settings.pear_port, server_rcv_q, 8)
    
    threading.Thread(target=rcv_comm, args=(client, client_rcv_q,), daemon=True).start()
    threading.Thread(target=rcv_comm, args=(file_server, server_rcv_q,), daemon=True).start()

    # sending main server client's mac
    send_mac()

    while True:
        pass
