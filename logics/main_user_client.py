from comms import client_comm
import queue

if __name__ == '__main__':

    rcv_q = queue.Queue()
    server = client_comm.ClientComm('127.0.0.1', 2000, rcv_q, )