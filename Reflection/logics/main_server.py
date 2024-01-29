import queue
from comms import server_comm
from database import db
from protocols import server_protocol as protocol


def handle_register(ip, vars):
    """
    gets ip and vars and adds user to db and returns response by protocol
    :param ip: ip
    :param vars:
    :return:
    """
    user, password = vars
    to_send = protocol.pack_status_register(db.add_user(user, password))
    server_comm.send(ip, to_send)

if __name__ == '__main__':
    rcv_q = queue.Queue()
    server_port = 2000
    server_comm = server_comm.ServerComm(server_port, rcv_q, 6)
    commands = {'1': handle_register}
    ip_mac = {}
    user_comps = {}
    username_ip = {}
    db = db.Db()
    while True:

        got = rcv_q.get()
        ip, data = got
        data = protocol.unpack(data)
        if not data or not ip:
            print('got error from server_comm')
            continue

        opcode, params = data
        commands[opcode](ip, params)
