import socket
import sys
from encryption import asymmetric_encryption

server = socket.socket()

server.bind(('0.0.0.0', 1500))

server.listen(3)
encryption = asymmetric_encryption.AsymmetricEncryption()

while True:
    new_client, addr = server.accept()
    print(f'{addr[0]}, connect to the server!')
    new_client.send(encryption.get_public_key())
    data = new_client.recv(1024)
    print(encryption.decrypt_msg(data))
