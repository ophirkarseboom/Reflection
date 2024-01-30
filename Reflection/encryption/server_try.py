import socket

from encryption import asymmetric_encryption
from encryption import symmetrical_encryption

server = socket.socket()

server.bind(('0.0.0.0', 1500))

server.listen(3)
encryption = asymmetric_encryption.AsymmetricEncryption()

while True:
    new_client, addr = server.accept()
    print(f'{addr[0]}, connect to the server!')
    new_client.send(encryption.get_public_key())
    data = new_client.recv(1024)
    key = encryption.decrypt_msg(data)
    symm = symmetrical_encryption.SymmetricalEncryption(key)
    new_client.send(symm.encrypt('hello world'))
