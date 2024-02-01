import queue
import threading

from Reflection.comms import client_comm
from Reflection.protocols import general_client_protocol as protocol
from uuid import getnode
import sys

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


def send_mac():
    """
    sends the mac to server
    """
    to_send = protocol.pack_mac(get_mac_address())
    client.send(to_send)


def handle_status_mac(vars):
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
        sys.exit()


if __name__ == '__main__':
    client_rcv_q = queue.Queue()
    server_ip = '192.168.4.96'
    port = 2000
    client = client_comm.ClientComm(server_ip, port, client_rcv_q, 6, 'G')
    commands = {'34': handle_status_mac}

    threading.Thread(target=rcv_comm, args=(client_rcv_q,), daemon=True).start()
    send_mac()
    while True:
        pass
