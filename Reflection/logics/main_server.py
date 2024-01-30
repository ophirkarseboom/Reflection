import queue

from Reflection.comms import server_comm
from Reflection.database import db
from Reflection.protocols import server_protocol as protocol
from Reflection.encryption import symmetrical_encryption


def handle_disconnect(ip:str, called_by_server_comm: bool):
    """
    disconnect client by ip and removes from dictionaries
    :param ip: ip address
    :return: None
    """

    # calls send_remove to all users related to ip
    # tbd

    if ip in ip_mac:
        del ip_mac[ip]

    if ip in user_comps:
        del user_comps[ip]

    if ip in username_ip.values():
        for key in username_ip.keys():
            if username_ip[key] == ip:
                del username_ip[key]
                break


    if not called_by_server_comm:
        server_comm.disconnect_client(ip)
        rcv_q.get()

def handle_register(ip, vars):
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

def handle_sign_in(user_ip, vars):
    """
    signs in the user and returns response accordingly
    :param user_ip: user's ip
    :param vars: username, password, mac address
    :return: None
    """

    if len(vars) != 3:

        handle_disconnect(user_ip, False)
        return
    user, password, mac = vars
    db_pass = db.get_password(user)
    hashed_pass = symmetrical_encryption.SymmetricalEncryption.hash(password)
    print('hashed_pass:', hashed_pass)
    print('db_pass:', db_pass)
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


        db.add_user_mac(user, mac)

    else:
        server_comm.send(user_ip, protocol.pack_status_login(False))

if __name__ == '__main__':
    rcv_q = queue.Queue()
    server_port = 2000
    server_comm = server_comm.ServerComm(server_port, rcv_q, 6)
    commands = {'01': handle_register, '03': handle_sign_in}
    ip_mac = {}
    user_comps = {}
    username_ip = {}
    db = db.Db()
    while True:

        got = rcv_q.get()
        ip, data = got
        if data == 'close':
            handle_disconnect(ip, True)
        data = protocol.unpack(data)
        if not data or not ip:
            print('got error from server_comm')
            continue

        opcode, params = data
        print(opcode, params)
        if opcode in commands:
            commands[opcode](ip, params)
        else:
            handle_disconnect(ip, False)