import socket
import threading
import sys
import time
from Project.encryption import symmetrical_encryption
from Project.encryption import asymmetric_encryption
from Project.protocols import general_client_protocol
import queue
from Project.protocols import user_client_protocol


class ClientComm:
    file_receive_opcodes = ('17', '18')
    def __init__(self, server_ip, port, rcv_q, send_len):
        self.send_len = send_len
        self.server_ip = server_ip
        self.port = port
        self.rcv_q = rcv_q
        self.socket = socket.socket()
        self.a_encrypt = asymmetric_encryption.AsymmetricEncryption()
        self.symmetric = None
        threading.Thread(target=self._main_loop, daemon=True).start()
        time.sleep(0.3)

    def _main_loop(self):

        try:
            self.socket.connect((self.server_ip, self.port))
        except Exception as e:
            sys.exit("server is down, try again later")
        while True:
            try:
                length = int(self.socket.recv(self.send_len).decode())
                data = self.socket.recv(length)

            except Exception as e:
                sys.exit("server is down, try again later")

            else:
                if self.symmetric:
                    data = self.symmetric.decrypt(data)
                    if data[:2] in self.file_receive_opcodes:
                        threading.Thread(target=self._receive_file(data))
                    else:
                        self.rcv_q.put(data)

                # key exchange
                else:
                    self._key_exchange(data[2:])


    def _receive_file(self, header):
        pass

    def _key_exchange(self, public_key):
        """
        gets server's public key and sends server symmetric key
        :param public_key: server's public key
        :return: None
        """

        self.symmetric = symmetrical_encryption.SymmetricalEncryption()
        self.send(general_client_protocol.pack_key(self.symmetric.key), public_key)


    def send(self, data, receiver_key=None):
        """
        sending data to server
        :param is_file: sending a file or not
        :param data: data to send
        :param receiver_key: if using asymmetric encryption using receiver key
        :return:
        """
        print(f'sending: {data}')
        if receiver_key:
            data = self.a_encrypt.encrypt_msg(data, receiver_key)
        elif self.symmetric:
            data = self.symmetric.encrypt(data)
            print(f'sending encrypted: {data}')
        else:
            sys.exit("couldn't set up key exchange")

        try:
            self.socket.send(str(len(data)).zfill(self.send_len).encode())
            self.socket.send(data)
        except Exception as e:
            print('client comm - send', str(e))
            sys.exit("server is down, try again later")


if __name__ == '__main__':
    rcv_q = queue.Queue()
    server = ClientComm('127.0.0.1', 2500, rcv_q, 8)
    file_name = r'C:\cyber\reflection\Project\comms\g2.jpg'
    with open(file_name, 'rb') as f:
        b = f.read()
    server.send(user_client_protocol.pack_change_file(file_name, len(b)))
    server.send(b)
    while True:
        if not rcv_q.empty():
            print(rcv_q.get())
