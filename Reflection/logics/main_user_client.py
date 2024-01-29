from comms import client_comm
import queue
import threading
from protocols import user_client_protocol as protocol


def rcv_comm(q):
    """
    gets data from server and calls functions accordingly
    :param : client comm
    """
    while True:
        data = protocol.unpack(rcv_q.get())
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
    if success:
        print('registered')
    else:
        print('could not register')


def do_register(username, password):
    """
    gets username and password and sends it to server by protocol
    :param username: username
    :param password: password
    :return: None
    """
    to_send = protocol.pack_register(username, password)
    client.send(to_send)
    print('hi')

if __name__ == '__main__':
    rcv_q = queue.Queue()
    client = client_comm.ClientComm('127.0.0.1', 2000, rcv_q, 6)
    commands = {'2': handle_status_register}
    threading.Thread(target=rcv_comm(client_comm), daemon=True).start()
    do_register('yotam_king', '1234')
    while True:
        pass
