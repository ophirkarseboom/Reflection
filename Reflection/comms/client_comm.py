import base64
import queue
import socket
import sys
import threading
import time
import os


from Reflection.encryption import asymmetric_encryption
from Reflection.encryption import symmetrical_encryption
from Reflection.protocols import general_client_protocol
from Reflection.protocols import user_client_protocol
from Reflection.local_handler.file_handler import FileHandler
from Reflection.settings import Settings
from Reflection.encryption.asymmetric_encryption import AsymmetricEncryption
import Reflection.protocols.user_client_protocol as user_client_protocl


class ClientComm:

    main_server_port = 2000
    file_receive_opcodes = ('17', '18')
    def __init__(self, server_ip, port, rcv_q, send_len, client_type=None):
        self.send_len = send_len
        self.server_ip = server_ip
        self.port = port
        self.rcv_q = rcv_q
        self.client_type = client_type

        self.server = socket.socket()

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

        self._key_exchange()
        while True:
            try:
                length = int(self.server.recv(self.send_len).decode())
                data = self.server.recv(length)
            except Exception as e:
                sys.exit("server is down, try again later")

            else:
                data = self.symmetric.decrypt(data)
                if data[:2] in self.file_receive_opcodes:
                    threading.Thread(target=self._receive_file(data))
                else:
                    self.rcv_q.put(data)


    def _receive_file(self, header):
        """
        gets header of file, receives file
        :param header: header of file
        :return: None
        """
        print('header:', header)
        if header[2:] == 'no':
            self.rcv_q.put(header)
            return
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
                file = self.symmetric.decrypt(file, True)

                print('header:', header)
                path = header.split(',')[1]
                path, name = FileHandler.split_path_last_part(path)
                if FileHandler.root in path:
                    path = path.replace(FileHandler.root, Settings.local_changes_path, 1)
                    print('path:', path)
                    # creating folder for file
                    FileHandler.create(path, 'fld')

                    # creating file
                    path += '\\' + name
                    with open(path, 'wb') as save:
                        save.write(file)

                    self.rcv_q.put(general_client_protocol.pack_status_open_file(True, path))


    def _key_exchange(self):
        """
        gets server's public key and sends server symmetric key
        :return: None
        """
        try:
            length = int(self.server.recv(self.send_len).decode())
            data = self.server.recv(length)

        except Exception as e:
            sys.exit("server is down, try again later")

        public_key = data[2:]
        print('pulic key:', public_key)
        self.symmetric = symmetrical_encryption.SymmetricalEncryption()
        key_to_send = general_client_protocol.pack_key(self.symmetric.key)
        key_to_send = AsymmetricEncryption.encrypt_msg(key_to_send, public_key)
        try:
            self.server.send(str(len(key_to_send)).zfill(self.send_len).encode())
            self.server.send(key_to_send)
        except Exception as e:
            sys.exit('could not send server key encrypted')

        if self.port == self.main_server_port and self.client_type:
            self._send_client_type()



    def _send_client_type(self):
        """
        sends server client type
        """
        self.send(general_client_protocol.pack_client_type(self.client_type))


    def send(self, data):
        """
        sending data to server
        :param data: data to send
        :return: None
        """
        print(f'sending: {data}')
        if self.symmetric:
            data = self.symmetric.encrypt(data)

        # try:
        print(f'data to send: {str(len(data)).zfill(self.send_len).encode() + data}')
        self.server.send(str(len(data)).zfill(self.send_len).encode() + data)
        # except Exception as e:
        #     print('client comm - send', str(e))
        #     sys.exit("server is down, try again later")

    def send_file(self, path, data):
        """
        sends file to server
        :param path: path of the file
        :param data: the data of the file (binary)
        :return: None
        """
        header = user_client_protocl.pack_change_file(path)
        header = self.symmetric.encrypt(header)
        data = self.symmetric.encrypt(data)
        header_len = str(len(header)).zfill(self.send_len).encode()
        data_len = str(len(data)).zfill(self.send_len).encode()
        try:
            self.server.send(header_len + header + data_len + data)
        except Exception as e:
            print('client comm - send file', str(e))
            sys.exit("server is down, try again later")



if __name__ == '__main__':
    rcv_q = queue.Queue()
    server = ClientComm('127.0.0.1', 2500, rcv_q, 8)
    server.send('05hi')
    while True:
        if not rcv_q.empty():
            data = rcv_q.get()
            data = user_client_protocol.unpack(data)
            os.system('start "" "' + data[0] + '"')
