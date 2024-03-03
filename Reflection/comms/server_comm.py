import base64
import queue
import socket
import threading

import select
from Reflection.encryption import asymmetric_encryption
from Reflection.encryption import symmetrical_encryption
from Reflection.protocols import general_client_protocol
from Reflection.protocols import server_protocol
from Reflection.settings import Settings


class ServerComm:

    main_server_port = Settings.server_port
    file_receive_opcodes = ('17', '18')
    def __init__(self, port, rcv_q, send_len):

        self.port = port
        self.rcv_q = rcv_q
        self.send_len = send_len
        self.socket = socket.socket()
        # socket: ip
        self.open_clients = {}
        self.a_encrypt = asymmetric_encryption.AsymmetricEncryption()
        self.is_running = False
        self.receiving_files = []
        self.my_ip = Settings.get_ip()
        threading.Thread(target=self._main_loop).start()

    def _main_loop(self):
        """
        waiting for clients to connect and puts in queue messages got from clients
        """
        self.socket.bind(("0.0.0.0", self.port))
        self.socket.listen(3)
        self.is_running = True
        while self.is_running:
            rlist, wlist, xlist = select.select(([self.socket]) + list(self.open_clients.keys()),
                                                list(self.open_clients.keys()), [], 0.03)
            # new client
            for current_socket in rlist:
                if current_socket is self.socket:

                    client, addr = self.socket.accept()
                    print(f'{addr[0]} connected!')
                    threading.Thread(target=self._key_exchange, args=(client, addr[0])).start()
                    continue

                # exist client
                if current_socket in self.receiving_files:
                    continue
                try:
                    length = int(current_socket.recv(self.send_len).decode())
                    data = current_socket.recv(length)
                except Exception as e:
                    print("main server in server comm: " + str(e))
                    self.disconnect_client(current_socket)
                else:
                    # exchanged keys already
                    if current_socket in self.open_clients:
                        encryption = self.open_clients[current_socket][1]
                        data = encryption.decrypt(data)

                    if data[:2] in self.file_receive_opcodes:
                        self.receiving_files.append(current_socket)
                        threading.Thread(target=self._receive_file(current_socket, data))

                    else:
                        print(f'data: {data}')
                        self.rcv_q.put((self.open_clients[current_socket][0], data))


    def _receive_file(self, client, header):
        """
        gets socket of client and header of file, receives file
        :param client: socket of client
        :param header: header of file
        :return: None
        """

        try:
            data_len = int(client.recv(self.send_len).decode())
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
                        file.extend(client.recv(1024))
                    except Exception as e:
                        self.disconnect_client(client)
                        print('error in receiving file:', str(e))
                        file_is_ok = False

                else:
                    try:
                        file.extend(client.recv(size))
                    except Exception as e:
                        self.disconnect_client(client)
                        print('error in receiving file:', str(e))
                        file_is_ok = False

            if file_is_ok:

                file = bytes(file)
                print(file)
                file = self.open_clients[client][1].decrypt(file, True)
                path = header.split(',')[1]
                ip = '\\' + self.my_ip
                if ip in path:

                    path = path.replace(ip, '')

                    # creating file
                    with open(path, 'wb') as save:
                        save.write(file)

        if client in self.receiving_files:
            self.receiving_files.remove(client)

    def disconnect_client(self, ip, from_logic=False):
        """
        gets client or ip to disconnect informs server and calls _disconnect_client
        :param ip: ip to disconnect
        :param from_logic: is called from logic
        :return: None
        """
        if type(ip).__name__ == 'str' or type(ip).__name__ == 'tuple':
            client = self._find_socket_by_ip(ip)
        else:
            client = ip
            if ip in self.open_clients:
                ip = self.open_clients[client][0]

        if not from_logic:
            self.rcv_q.put((ip, 'close'))
        self._disconnect_client(client)

    def _disconnect_client(self, client):
        """
        gets ip, deletes ip from all dictionaries and closes it's socket
        :param client: client socket
        :return: None
        """
        if client in self.open_clients:
            print(f'{self.open_clients[client][0]} - disconnected')
            del self.open_clients[client]

        if client in self.receiving_files:
            self.receiving_files.remove(client)

        if client:
            print(client)
            client.close()

    def _key_exchange(self, client, ip):
        """
        exchanging keys with client, puts client in open clients at the end
        :param client: client socket
        :param ip: ip address
        :return:
        """
        self.send(client, server_protocol.pack_public_key(self.a_encrypt.get_public_key()), False)
        try:
            length = int(client.recv(self.send_len).decode())
            data = client.recv(length)
            data = self.a_encrypt.decrypt_msg(data)
        except Exception as e:
            print("error in key_exchange: " + str(e))
            self.disconnect_client(client)
        else:

            self.open_clients[client] = [ip, symmetrical_encryption.SymmetricalEncryption(data[2:])]

            # main server
            if self.port == self.main_server_port:
                self._get_client_type(client, ip)

    def _get_client_type(self, client, ip):
        """
        receives client type from client
        :param client: socket of client
        :param ip: ip of client
        :return: None
        """
        try:
            length = int(client.recv(self.send_len).decode())
            data = client.recv(length)
            print('data:', data)
        except Exception as e:
            print("error in key_exchange: " + str(e))
            self.disconnect_client(client)
        else:
            encryption = self.open_clients[client][1]
            data = encryption.decrypt(data)
            typ = data[-1]
            if typ != 'G' and typ != 'U':
                self.disconnect_client(client)
            else:
                self.open_clients[client][0] = (ip, typ)
                print('finished transferring client type')


    def _find_socket_by_ip(self, ip):
        """
        gets ip and returns the socket matched
        :param ip: ip got (string)
        :return: socket matched (socket)
        """
        client = None
        for soc in self.open_clients.keys():
            if self.open_clients[soc][0] == ip:

                client = soc
                break
        return client

    def send(self, ip, data, encrypt=True):
        """
        sending ip a msg
        :param ip: the ip to send to and general or user
        :param data: data to send
        :param encrypt: to encrypt data or not
        :return: None
        """
        if type(ip).__name__ == 'str' or type(ip).__name__ == 'tuple':
            sock = self._find_socket_by_ip(ip)
        else:
            sock = ip

        if sock and self.is_running:

            print(f'sending to {ip}:', data)
            if encrypt and sock in self.open_clients:
                encryption = self.open_clients[sock][1]
                data = encryption.encrypt(data)

            try:
                sock.send(str(len(data)).zfill(self.send_len).encode())
                sock.send(data)
            except Exception as e:
                print('server comm - send', str(e))
                self.disconnect_client(sock)

    def close_server(self):
        self.is_running = False




if __name__ == '__main__':
    msg_q = queue.Queue()
    server = ServerComm(2500, msg_q, 8)
    file_name = r'T:\public\cyber\ophir\Reflection\Reflection\comms\cat.jpg'
    with open(file_name, 'rb') as f:
        b = f.read()


    while True:
        if not msg_q.empty():

            data = msg_q.get()
            print(f'sending {data[0]}')
            server.send(data[0], general_client_protocol.pack_status_open_file(True))
            server.send(data[0], b)
