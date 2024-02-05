import queue

from Reflection.comms import server_comm
from Reflection.database import db
from Reflection.protocols import server_protocol as protocol
from Reflection.encryption import symmetrical_encryption
import os



def handle_disconnect(client_ip:str, called_by_server_comm: bool):
    """
    disconnect client by ip and removes from dictionaries
    :param client_ip: ip address
    :return: None
    """

    # calls send_remove to all users related to ip
    # tbd

    if client_ip in ip_mac:
        del ip_mac[client_ip]

    if client_ip in user_comps:
        del user_comps[client_ip]

    for ip in user_comps:
        if client_ip in user_comps[ip]:
            user_comps[ip].remove(client_ip)

    if client_ip in username_ip.values():
        for key in username_ip.keys():
            if username_ip[key] == client_ip:
                del username_ip[key]
                break

    if not called_by_server_comm:
        server_comm.disconnect_client(client_ip)
        rcv_q.get()

def handle_register(ip: str, vars: list):
    """
    gets ip and vars and adds user to db and returns response by protocol
    :param ip: ip
    :param vars:
    :return:
    """
    if len(vars) != 2:
        handle_disconnect(ip, False)
        return
    user, password = vars
    to_send = protocol.pack_status_register(db.add_user(user, password))
    server_comm.send(ip, to_send)

def handle_sign_in(user_ip: str, vars: list):
    """
    signs in the user and returns response accordingly
    :param user_ip: user's ip
    :param vars: username, password, mac address
    :return: None
    """

    if len(vars) != 3:

        handle_disconnect(user_ip, False)
        return
    user, password, user_mac = vars
    db_pass = db.get_password(user)
    hashed_pass = symmetrical_encryption.SymmetricalEncryption.hash(password)
    if db_pass == hashed_pass:
        server_comm.send(user_ip, protocol.pack_status_login(True))
        macs_worked_on = db.get_macs(user)
        user_comps[user_ip] = []
        username_ip[user] = user_ip
        for mac in macs_worked_on:
            for ip in ip_mac:
                if ip_mac[ip] == mac:
                    user_comps[user_ip].append(ip)
                    # call transition_file_tree
                    server_comm.send(ip, protocol.pack_ask_file_Tree(f'{user}\\{ip}'))

        print(f'user:{user},mac:{user_mac}')
        print('adding_mac:', db.add_user_mac(user, user_mac))
        print('ip_mac:', ip_mac)
        print('user_comps:', user_comps)
        print('username_ip:', username_ip)
    else:
        server_comm.send(user_ip, protocol.pack_status_login(False))



def handle_got_file_tree(got_ip, vars: list):
    """

    :param got_ip: the ip got file tree from
    :param vars: file tree got from got_ip
    :return: None
    """

    file_tree = vars[0]
    got_ok = True
    if len(vars) == 1 and '?' in file_tree:
        user_to_send = os.path.basename(file_tree[:file_tree.index('?')])
        ip_to_send = username_ip[user_to_send]
        if ip_to_send in user_comps and got_ip in user_comps[ip_to_send]:
            server_comm.send(ip_to_send, protocol.pack_send_file_tree(file_tree, got_ip))
        else:
            got_ok = False
    else:
        got_ok = False

    if not got_ok:
        handle_disconnect(got_ip, False)

def handle_got_mac(client_ip: str, vars: list):
    """
    get mac from ip adds it to ip_mac and ip to user_comps and sends status back
    :param client_ip: client's ip
    :param vars: mac address
    :return: None
    """
    if len(vars) != 1:
        handle_disconnect(client_ip, False)
        return

    mac = vars[0]
    users_for_mac = db.get_users(mac)
    has_users = len(users_for_mac) > 0
    if has_users:
        ip_mac[client_ip] = mac
        ip_for_mac = [username_ip[user] for user in users_for_mac if user in username_ip]
        for ip in ip_for_mac:
            if ip in user_comps:
                user_comps[ip].append(client_ip)

                # get user by ip
                user = next(filter(lambda item: item[1] == ip, username_ip.items()), None)

                server_comm.send(client_ip, protocol.pack_ask_file_Tree(user))

    server_comm.send(client_ip, protocol.pack_status_mac(has_users))



if __name__ == '__main__':
    rcv_q = queue.Queue()
    server_port = 2000
    server_comm = server_comm.ServerComm(server_port, rcv_q, 6)
    commands = {'01': handle_register, '03': handle_sign_in, '20': handle_got_file_tree, '29': handle_got_mac}
    ip_mac = {}
    user_comps = {}
    username_ip = {}
    db = db.Db()
    while True:

        got = rcv_q.get()
        ip, data = got
        print('data:', data)
        if data == 'close':
            handle_disconnect(ip, True)
            continue

        data = protocol.unpack(data)
        if not data or not ip:
            print('got error from server_comm')
            continue

        opcode, params = data
        if opcode in commands:
            commands[opcode](ip, params)
        else:
            print('opcode is not on list')
            handle_disconnect(ip, False)