import socket
import threading
import sys
import time
from classes import symmetrical_encryption
from classes import asymmetric_encryption


class ClientComm:
    def __init__(self, server_ip, port, recv_q):
        self.server_ip = server_ip
        self.port = port
        self.recv_q = recv_q
        self.socket = socket.socket()
        self.encrypt = None
        self.a_encrypt = asymmetric_encryption.AsymmetricEncryption()
        threading.Thread(target=self._main_loop, daemon=True).start()
        time.sleep(0.3)

    def _main_loop(self):

        try:
            self.socket.connect((self.server_ip, self.port))
        except Exception as e:
            sys.exit("server is down, try again later")
        while True:
            try:
                len = int(self.socket.recv(3).decode())
                data = self.socket.recv(len)
                if self.encrypt:
                    data = self.encrypt.decrypt_msg(data)
                    command = data[:2]
                else:
                    self.encrypt = symmetrical_encryption.SymmetricalEncryption()
                    command = data[:2].decode()


            except Exception as e:
                sys.exit("server is down, try again later")
            else:
                data = data[2:]
                self.recv_q.put((command, data))

    def send(self, command: str, data, receiver_key=None):
        """
        sending something to server
        :param command: a string
        :param data: the data of the command
        :param receiver_key: if using asymmetric encryption using receiver key
        :return:
        """
        command = command.zfill(2)
        if command == '99':
            if receiver_key:
                data = self.a_encrypt.encrypt_msg(b'99'+data, receiver_key)
            else:
                raise ValueError('has to get receiver key if command equals 99')
        else:
            data = command+data
            data = self.encrypt.encrypt_msg(data)
        try:
            self.socket.send(str(len(data)).zfill(3).encode())
            self.socket.send(data)
        except Exception as e:
            print('client comm - send', str(e))
            sys.exit("server is down, try again later")
