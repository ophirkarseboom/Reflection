import socket
import sys
from encryption import asymmetric_encryption

server = socket.socket()
try:
    server.connect(('127.0.0.1', 1500))
except Exception as e:
    print(str(e))
    server.close()
    sys.exit('error')


key = server.recv(1024)
asymmetric = asymmetric_encryption.AsymmetricEncryption()
data = asymmetric.encrypt_msg('hello world', key)
server.send(data)
