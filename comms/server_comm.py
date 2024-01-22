import select
import socket
import threading
import queue
from encryption import asymmetric_encryption
from encryption import symmetrical_encryption


class ServerComm:
    count = 0

    def __init__(self, port, rcv_q, send_len):

        self.port = port
        self.rcv_q = rcv_q
        self.send_len = send_len
        self.socket = socket.socket()
        # socket: ip
        self.open_clients = {}
        self.a_encrypt = asymmetric_encryption.AsymmetricEncryption()
        self.is_running = False
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
                    if GameHandle.game_running or len(self.open_clients.keys()) > 3:
                        continue
                    client, addr = self.socket.accept()
                    print(f'{addr[0]} connected!')
                    threading.Thread(target=self._key_exchange(client, addr))
                    continue

                # exist client
                try:
                    length = int(current_socket.recv(3).decode())
                    data = current_socket.recv(length)
                except Exception as e:
                    print("main server in server comm: " + str(e))
                    self.disconnect_client(current_socket)
                else:
                    # exchanged keys already
                    if current_socket in self.open_clients:
                        encryption = self.keys[current_socket]
                        data = encryption.decrypt_msg(data)
                        command = data[:2]
                        data = data[2:]
                        print(f'data: {data}')
                        self.rcv_q.put((self.open_clients[current_socket], command, data))

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

    def _disconnect_client(self, client: socket):
        """
        gets ip, deletes ip from all dictionaries and closes it's socket
        :param client: client socket
        :return: None
        """
        if client in self.open_clients:
            print(f'{self.open_clients[client][0]} - disconnected')
            del self.open_clients[client]

        client.close()

    def _key_exchange(self, client, addr):
        """
        exchanging keys with client, puts client in open clients at the end
        """
        self.count += 1
        self.send(client, '99', self.a_encrypt.get_public_key())
        try:
            length = int(client.recv(3).decode())
            data = client.recv(length)
        except Exception as e:
            print("error in key_exchange: " + str(e))
            self.disconnect_client(client)
        else:
            data = self.a_encrypt.decrypt_msg(data)
            self.keys[client] = symmetrical_encryption.SymmetricalEncryption(data[2:])
            print(addr[0])
            self.open_clients[client] = addr[0] + str(self.count)

    def _find_socket_by_ip(self, ip):
        '''
        gets ip and returns the socket matched
        :param ip: ip got (string)
        :return: socket matched (socket)
        '''
        client = None
        for soc in self.open_clients.keys():
            if self.open_clients[soc][0] == ip:
                client = soc
                break
        return client

    def send(self, ip, command: str, data):
        """
        sending a client a msg
        :param ip: the ip to send to
        :param command: a string
        :param data: a string
        :return: None
        """
        if type(ip).__name__ == 'str':
            sock = self._find_socket_by_ip(ip)
        else:
            sock = ip

        if self.is_running:
            command = command.zfill(2)
            if sock:
                if command == '99':
                    command = command.encode()
                    data = command + data
                else:
                    if sock not in self.keys:
                        return

                    print(f'sending to {self.open_clients[sock]}:', command, data)
                    encryption = self.keys[sock]
                    data = command + data
                    data = encryption.encrypt_msg(data)
                try:
                    sock.send(str(len(data)).zfill(3).encode())
                    sock.send(data)
                except Exception as e:
                    print('server comm - send', str(e))
                    self.disconnect_client(sock)

    def close_server(self):
        self.is_running = False

    def is_running(self):
        return self.is_running


if __name__ == '__main__':
    msg_q = queue.Queue()
    server = ServerComm(10000, msg_q)
