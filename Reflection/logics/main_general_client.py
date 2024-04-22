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
    commands = {'23': handle_delete, '16': handle_open_file, '21': handle_rename, '25': move_from_server,
                '27': clone_from_server, '18': handle_changed_file, '31': handle_asked_file_tree,
                '32': handle_create, '34': handle_status_mac, '36':clone_from_client, '37': handle_status_clone,
                '38': move_from_client, '39': handle_status_move}
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
            break

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
    server.send(got_ip, client_protocol.pack_status_change_file(status, path))

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

def handle_create(client_got: ClientComm, vars: list):
    """
    creates what server sent if possible and returns status
    :param client_got: client comm
    :param vars: location of creation and it's type
    :return: None
    """
    location, typ = vars
    status = FileHandler.create(location, typ)
    client_got.send(client_protocol.pack_status_create(status, location, typ))

def handle_rename(client_got: ClientComm, vars: list):
    """
    renames a file\folder
    :param client_got: client comm
    :param vars: location of object to rename and the new name
    :return: None
    """
    location, new_name = vars
    status = FileHandler.rename(location, new_name)
    client_got.send(client_protocol.pack_status_rename(status, location, new_name))


def clone_from_server(client_got: ClientComm, vars: list):
    """
    clones a file
    :param client_got: client comm
    :param vars: location of object to clone and the new location
    :return: None
    """
    copy_from, copy_to = vars
    username = FileHandler.get_user(copy_from)

    copy_to_ip = FileHandler.extract_ip(username, copy_to)
    my_ip = FileHandler.extract_ip(username, copy_from)

    # locally cloning file
    if my_ip == copy_to_ip:
        local_copy_from = FileHandler.remove_ip(username, copy_from)
        local_copy_to = FileHandler.remove_ip(username, copy_to)

        status = FileHandler.direct_copy_file(local_copy_from, local_copy_to)
        client_got.send(client_protocol.pack_status_clone_to_server(status, copy_from, copy_to))

    # sending file to other computer
    else:
        rcv_q = Queue()

        comm = ClientComm(copy_to_ip, Settings.pear_port, rcv_q, 8, 'G')
        threading.Thread(target=rcv_comm, args=(comm, rcv_q), daemon=True).start()
        local_file_data = FileHandler.remove_ip(username, copy_from)
        with open(local_file_data, 'rb') as f:
            file_data = f.read()

        header = client_protocol.pack_do_clone(copy_to, copy_from)
        comm.send_file(header, file_data)


def clone_from_client(got_ip: str, server: ServerComm, vars: list):
    """
    saves file in right position after cloned and informing client
    :param got_ip: the ip got the file from
    :param server: the comm
    :param vars:
    """
    print('got_ip:', got_ip)
    if len(vars) != 3:
        print('amount of vars is not valid')
        server.disconnect_client(got_ip, True)
        return

    status, copy_to, copy_from = vars
    status = (status == 'ok')
    server.send(got_ip, client_protocol.pack_status_clone_to_client(status, copy_to, copy_from))


def handle_status_clone(client_got: ClientComm, vars: list):
    """
    informing server if cloned file worked
    :param client_got: the comm
    :param vars: status, new_path, old_path
    """
    if len(vars) != 3:
        print('amount of vars is not valid')
        client_got.close()
        return

    status, copied_to, copied_from = vars
    status = (status == 'ok')

    # informing server and closing connection to client
    client.send(client_protocol.pack_status_move_to_server(status, copied_from, copied_to))
    client_got.close()

def handle_status_move(client_got: ClientComm, vars: list):
    """
    informing server if moved file worked and finishing moving if needed
    :param client_got: the comm
    :param vars: status, new_path, old_path
    """
    if len(vars) != 3:
        print('amount of vars is not valid')
        client_got.close()
        return

    status, moved_to, moved_from = vars
    status = (status == 'ok')

    # completing moving
    if status:
        username = FileHandler.get_user(moved_from)
        local_moved_from = FileHandler.remove_ip(username, moved_from)
        FileHandler.delete(local_moved_from)

    # informing server and closing connection to client
    client.send(client_protocol.pack_status_move_to_server(status, moved_from, moved_to))
    client_got.close()

def move_from_client(got_ip: str, server: ServerComm, vars: list):
    """
    saves file in right position after moved and informing client
    :param got_ip: the ip got the file from
    :param server: the comm
    :param vars:
    """
    print('got_ip:', got_ip)
    if len(vars) != 3:
        print('amount of vars is not valid')
        server.disconnect_client(got_ip, True)
        return

    status, move_to, move_from = vars
    status = (status == 'ok')
    server.send(got_ip, client_protocol.pack_status_move_to_client(status, move_to, move_from))

def move_from_server(client_got: ClientComm, vars: list):
    """
    moves a file
    :param client_got: client comm
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
        client_got.send(client_protocol.pack_status_move_to_server(status, move_from, move_to))

    # sending file to other computer
    else:
        rcv_q = Queue()

        comm = ClientComm(move_to_ip, Settings.pear_port, rcv_q, 8, 'G')
        threading.Thread(target=rcv_comm, args=(comm, rcv_q), daemon=True).start()
        local_file_data = FileHandler.remove_ip(username, move_from)
        with open(local_file_data, 'rb') as f:
            file_data = f.read()

        header = client_protocol.pack_do_move(move_to, move_from)
        comm.send_file(header, file_data)


def handle_delete(client_got: ClientComm, vars: list):
    """
    deletes what server sent if possible and returns status to server
    :param client_got: client comm
    :param vars: location to delete
    :return: None
    """
    location = vars[0]
    status = FileHandler.delete(location)
    client_got.send(client_protocol.pack_status_delete(status, location))


def send_mac():
    """
    sends the mac to server
    """
    to_send = client_protocol.pack_mac(Settings.get_mac_address())
    client.send(to_send)


def handle_status_mac(client_got: ClientComm, vars: list):
    """
    gets status and shows user what happened
    :param client_got: the client got
    :param vars: success or failure
    :return: None
    """
    success = vars[0]
    if success == 'ok':
        print('sent mac successfully')
    else:
        print("a user didn't login through this computer")


def handle_asked_file_tree(client_got: ClientComm, vars: list):
    """
    gets folder and sends server file tree of folder
    :param client_got: the comm got
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

        client_got.send(client_protocol.pack_file_tree(folder_path))


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
