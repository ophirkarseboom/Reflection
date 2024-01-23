import select
import socket
import threading
import queue
from Project.encryption import asymmetric_encryption
from Project.encryption import symmetrical_encryption
from Project.protocols import server_protocol



class ServerComm:

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
        threading.Thread(target=self._main_loop).start()

    def _main_loop(self):
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
                    threading.Thread(target=self._key_exchange(client, addr[0]))
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
                        print(self.receiving_files)
                        data = encryption.decrypt(data)

                    if data[:2] in self.file_receive_opcodes:
                        print('yessssssssssssssss!')
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
        header = server_protocol.unpack(header)
        print(header)
        print(len(header))
        if len(header) == 2:
            location, data_len = header[1]
            if data_len.isdigit():
                data_len = int(data_len)
                file_is_ok = True
                file = bytearray()
                while len(file) < data_len and file_is_ok:

                    size = data_len - len(file)
                    if size > 1024:
                        try:
                            file.extend(client.recv(1024))
                        except Exception as e:
                            self.disconnect_client(client)
                            print(str(e))
                            file_is_ok = False

                    else:
                        try:
                            file.extend(client.recv(size))
                        except Exception as e:
                            self.disconnect_client(client)
                            print(str(e))
                            file_is_ok = False

                if file_is_ok:

                    file = bytes(file)
                    print(file)
                    file = self.open_clients[client][1].decrypt(file, True)
                    with open(location+'1', 'wb') as picture:
                        picture.write(file)

                    self.rcv_q.put(self.open_clients[client][0], header+','+file)

        if client in self.receiving_files:
            self.receiving_files.remove(client)

    def disconnect_client(self, ip):
        """
        gets client or ip to disconnect informs server and calls _disconnect_client
        :param ip: ip to disconnect
        :return: None
        """
        if type(ip).__name__ == 'str':
            client = self._find_socket_by_ip(ip)
        else:
            client = ip
            if ip in self.open_clients:
                ip = self.open_clients[client][0]

        self.rcv_q.put(('close', ip))
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
        client.close()

    def _key_exchange(self, client, ip):
        """
        exchanging keys with client, puts client in open clients at the end
        :param client: client socket
        :param ip:
        :return:
        """
        self.send(client, server_protocol.pack_public_key(self.a_encrypt.get_public_key()), False)
        try:
            length = int(client.recv(self.send_len).decode())
            data = client.recv(length)
        except Exception as e:
            print("error in key_exchange: " + str(e))
            self.disconnect_client(client)
        else:
            data = self.a_encrypt.decrypt_msg(data)
            self.open_clients[client] = (ip, symmetrical_encryption.SymmetricalEncryption(data[2:]))



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
        :param ip: the ip to send to
        :param data: data to send
        :param encrypt: to encrypt data or not
        :return: None
        """
        if type(ip).__name__ == 'str':
            sock = self._find_socket_by_ip(ip)
        else:
            sock = ip

        if sock and self.is_running:
            print(f'sending to {ip}:', data)
            if encrypt and sock in self.open_clients:
                encryption = self.open_clients[sock][1]
                data = encryption.encrypt_msg(data)

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
    # while True:
    #     if not msg_q.empty():
    #         print(msg_q.get())
