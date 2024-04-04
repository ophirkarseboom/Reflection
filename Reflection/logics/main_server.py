import queue
from Reflection.settings import Settings
from Reflection.comms import server_comm
from Reflection.database import db
from Reflection.protocols import server_protocol as protocol
from Reflection.encryption import symmetrical_encryption
from Reflection.local_handler.file_handler import FileHandler
import re


def handle_disconnect(client_ip: str, called_by_server_comm: bool):
    """
    disconnect client by ip and removes from dictionaries
    :param client_ip: ip address
    :return: None
    """

    # calls to delete ip to all users related to ip
    for ip in user_comps:
        if client_ip in user_comps[ip]:
            username = get_key_by_value(username_ip, ip)
            server_comm.send(ip, protocol.pack_status_delete(True, f'{Settings.root}{username}\\{client_ip[0]}'))

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
        server_comm.disconnect_client(client_ip, True)

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
        user_comps[user_ip] = [(user_ip[0], 'G')]
        username_ip[user] = user_ip

        # adding to user comps
        for mac in macs_worked_on:
            for ip in ip_mac:
                if ip_mac[ip] == mac:
                    user_comps[user_ip].append(ip)
                    server_comm.send(ip, protocol.pack_ask_file_Tree(f'{user}'))

        # asking file tree from own user mac
        print('user_ip:', user_ip)
        print()
        if user_mac not in macs_worked_on:
            server_comm.send((user_ip[0], 'G'), protocol.pack_ask_file_Tree(f'{user}'))

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
        user_to_send = file_tree.split('\\')[2].split('?')[0]
        print('user_to_send:', user_to_send)
        if user_to_send in username_ip:
            ip_to_send = username_ip[user_to_send]
            print('to_send:', ip_to_send)


        else:
            got_ok = False
            ip_to_send = None

        if got_ok and ip_to_send in user_comps and got_ip in user_comps[ip_to_send]:

            result = replace_outside_brackets(file_tree, user_to_send, f'{user_to_send}\\{got_ip[0]}')

            # sending file tree to user
            server_comm.send(ip_to_send, protocol.pack_send_file_tree(result))
        else:
            got_ok = False
    else:
        got_ok = False

    if not got_ok:
        print('error in getting file tree')
        handle_disconnect(got_ip, False)


def replace_outside_brackets(input_str: str, string_to_replace: str, replacement: str):
    """
    replaces a certain string only outside brackets
    :param input_str: entire string
    :param string_to_replace: what to replace
    :param replacement: what ot replace it with
    :return: new string
    """
    result = ''
    inside_brackets = False
    index = 0

    while index < len(input_str):
        if input_str[index] == '[':
            inside_brackets = True
            result += input_str[index]
            index += 1
        elif input_str[index] == ']':
            inside_brackets = False
            result += input_str[index]
            index += 1
        elif input_str[index:index + len(string_to_replace)] == string_to_replace and not inside_brackets:
            result += replacement
            index += len(string_to_replace)
        else:
            result += input_str[index]
            index += 1

    return result

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
    ip_mac[client_ip] = mac
    if has_users:
        print('nice')
        ip_for_mac = [username_ip[user] for user in users_for_mac if user in username_ip]
        for ip in ip_for_mac:
            if ip in user_comps:
                user_comps[ip].append(client_ip)

                # get user by ip
                user = get_key_by_value(username_ip, ip)
                server_comm.send(client_ip, protocol.pack_ask_file_Tree(f'{user}'))

    server_comm.send(client_ip, protocol.pack_status_mac(has_users))


def got_create(got_ip: str, vars: str):
    """
    sending appropriate client to create object
    :param got_ip: ip sent from
    :param vars: location to create and typ of creation
    :return: None
    """

    if len(vars) != 2:

        handle_disconnect(got_ip, False)
        return

    location, typ = vars
    user_got = get_key_by_value(username_ip, got_ip)
    ip_to_send = FileHandler.extract_ip(user_got, location)
    ip_to_send = (ip_to_send, 'G')
    location = FileHandler.remove_ip(user_got, location)
    server_comm.send(ip_to_send, protocol.pack_do_create(location, typ))


def got_rename(got_ip: str, vars: str):
    """
    sending appropriate client to rename object
    :param got_ip: ip sent from
    :param vars: location of object to rename and name to rename it to
    :return: None
    """

    if len(vars) != 2:

        handle_disconnect(got_ip, False)
        return

    location, new_name = vars
    user_got = get_key_by_value(username_ip, got_ip)
    ip_to_send = FileHandler.extract_ip(user_got, location)
    ip_to_send = (ip_to_send, 'G')
    location = FileHandler.remove_ip(user_got, location)
    server_comm.send(ip_to_send, protocol.pack_do_rename(location, new_name))



def got_clone(got_ip: str, vars: str):
    """
    sending appropriate client to clone object
    :param got_ip: ip sent from
    :param vars: location of object to clone and place to clone to
    :return: None
    """

    if len(vars) != 2:

        handle_disconnect(got_ip, False)
        return

    copy_from, copy_to = vars
    user_got = get_key_by_value(username_ip, got_ip)
    ip_from = FileHandler.extract_ip(user_got, copy_from)
    ip_to = FileHandler.extract_ip(user_got, copy_to)
    if ip_from == ip_to:
        ip_to_send = (ip_from, 'G')
        path_from = FileHandler.remove_ip(user_got, copy_from)
        path_to = FileHandler.remove_ip(user_got, copy_to)
        server_comm.send(ip_to_send, protocol.pack_do_clone(path_from, path_to))


def handle_status_rename(got_ip: str, vars: str):
    """
    sending user if renaming was success
    :param got_ip: ip got from
    :param vars: status, location, new name
    :return: None
    """
    if len(vars) != 3:
        handle_disconnect(got_ip, False)
        return

    status, location, new_name = vars
    print('status:', status)
    username = location.replace(FileHandler.root, '')
    username = username[:username.index('\\')]

    ip_to_send = username_ip[username]
    location = FileHandler.insert_ip(location, username, got_ip[0])
    status = status == 'ok'
    server_comm.send(ip_to_send, protocol.pack_status_rename(status, location, new_name))

def handle_status_create(got_ip: str, vars: str):
    """
    sending user if creation was success
    :param got_ip: ip got from
    :param vars: status, location, typ
    :return: None
    """
    if len(vars) != 3:
        handle_disconnect(got_ip, False)
        return

    status, location, typ = vars
    print('location:', location)
    username = location.replace(FileHandler.root, '')
    username = username[:username.index('\\')]
    print('user:', username)

    ip_to_send = username_ip[username]
    location = FileHandler.insert_ip(location, username, got_ip[0])
    status = status == 'ok'
    server_comm.send(ip_to_send, protocol.pack_status_create(status, location, typ))

def handle_status_delete(got_ip: str, vars: str):
    """
    sending user if delete was success
    :param got_ip: ip got from
    :param vars: status, location
    :return: None
    """
    if len(vars) != 2:
        handle_disconnect(got_ip, False)
        return

    status, location = vars
    username = location.replace(FileHandler.root, '')
    username = username[:username.index('\\')]

    ip_to_send = username_ip[username]
    location = FileHandler.insert_ip(location, username, got_ip[0])
    status = status == 'ok'
    server_comm.send(ip_to_send, protocol.pack_status_delete(status, location))




def get_key_by_value(dic: dict, value: str):
    """
    gets value and returns key of value
    :param value: value in dic
    :return: key of value
    """
    return next(filter(lambda item: item[1] == value, dic.items()), None)[0]


def got_delete(got_ip: str, vars: list):
    """
    sending appropriate client to delete object
    :param got_ip: ip sent from
    :param vars: location to delete
    :return: None
    """
    if len(vars) != 1:

        handle_disconnect(got_ip, False)
        return

    location = vars[0]
    user_got = get_key_by_value(username_ip, got_ip)
    ip_to_send = FileHandler.extract_ip(user_got, location)
    ip_to_send = (ip_to_send, 'G')
    location = FileHandler.remove_ip(user_got, location)
    server_comm.send(ip_to_send, protocol.pack_do_delete(location))



if __name__ == '__main__':
    rcv_q = queue.Queue()
    server_port = 2000
    server_comm = server_comm.ServerComm(server_port, rcv_q, 6)
    commands = {'01': handle_register, '03': handle_sign_in, '06': got_create, '08': got_rename, '10': got_delete, '20': handle_got_file_tree, '22': handle_status_rename, '24': handle_status_delete, '29': handle_got_mac, '33': handle_status_create}
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