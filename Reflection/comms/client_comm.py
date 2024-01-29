import socket
import threading
import sys
import time
from encryption import symmetrical_encryption
from encryption import asymmetric_encryption
from protocols import general_client_protocol
import queue
from protocols import user_client_protocol
import base64


class ClientComm:
    file_receive_opcodes = ('17', '18')
    def __init__(self, server_ip, port, rcv_q, send_len):
        self.send_len = send_len
        self.server_ip = server_ip
        self.port = port
        self.rcv_q = rcv_q
        self.server = socket.socket()
        self.a_encrypt = asymmetric_encryption.AsymmetricEncryption()
        self.symmetric = None
        threading.Thread(target=self._main_loop, daemon=True).start()
        time.sleep(0.3)

    def _main_loop(self):
        """
        receives
        :return:
        """
        try:
            self.server.connect((self.server_ip, self.port))
        except Exception as e:
            sys.exit("server is down, try again later")
        while True:
            try:
                length = int(self.server.recv(self.send_len).decode())
                data = self.server.recv(length)

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
        """
        gets header of file, receives file
        :param header: header of file
        :return: None
        """

        try:
            data_len = int(self.server.recv(self.send_len).decode())
        except Exception as e:
            print('error in receiving file:', str(e))

        else:
            file_is_ok = True
            file = bytearray()

            # receiving file in parts
            while len(file) < data_len and file_is_ok:

                size = data_len - len(file)
                if size > 1024:
                    try:
                        file.extend(self.server.recv(1024))
                    except Exception as e:
                        print('error in receiving file:', str(e))
                        file_is_ok = False

                else:
                    try:
                        file.extend(self.server.recv(size))
                    except Exception as e:
                        print('error in receiving file:', str(e))
                        file_is_ok = False

            if file_is_ok:
                file = bytes(file)
                print(file)
                file = self.symmetric.decrypt(file, True)
                file = base64.b64encode(file).decode()
                self.rcv_q.put(str(header + ',' + file))


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
            self.server.send(str(len(data)).zfill(self.send_len).encode())
            self.server.send(data)
        except Exception as e:
            print('client comm - send', str(e))
            sys.exit("server is down, try again later")


if __name__ == '__main__':
    rcv_q = queue.Queue()
    server = ClientComm('127.0.0.1', 2500, rcv_q, 8)
    server.send('05hi')
    while True:
        if not rcv_q.empty():
            data = rcv_q.get()
            data = user_client_protocol.unpack(data)
            print('data:', data)
            file = base64.b64decode(data[1][1])
            print('file:', file)
            with open('try5.jpg', 'wb') as picture:
                picture.write(file)
