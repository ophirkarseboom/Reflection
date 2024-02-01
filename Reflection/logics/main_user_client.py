import queue
import threading

from Reflection.comms import client_comm
from Reflection.protocols import user_client_protocol as protocol
from uuid import getnode

def get_mac_address():
    """ returns  mac address"""
    return ':'.join(['{:02x}'.format((getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])

def rcv_comm(q):
    """
    gets data from server and calls functions accordingly
    :param : client comm
    """
    while True:
        data = protocol.unpack(q.get())
        if not data:
            print('got None from protocol')
            continue

        print('data from server:', data)
        opcode, params = data
        commands[opcode](params)

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

def handle_status_connect(vars):
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
    rcv_q = queue.Queue()
    server_ip = '192.168.4.96'
    port = 2000
    client = client_comm.ClientComm(server_ip, port, rcv_q, 6, 'U')

    commands = {'02': handle_status_register, '04': handle_status_connect}
    threading.Thread(target=rcv_comm, args=(rcv_q,), daemon=True).start()
    do_connect('ophir', '12345')

    while True:
        pass
