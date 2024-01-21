from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

class AsymmetricEncryption:

    def __init__(self, private_key=None, public_key=None):

        if not private_key and not public_key:
            key = RSA.generate(2048)
            self.public_key = key.publickey().export_key()
            self.private_key = key.export_key()
        elif not private_key or not public_key:
            self.private_key = private_key
            self.public_key = public_key
        else:
            raise ValueError('Either provide two arguments or none')

    def encrypt_msg(self, msg, receiver_key):
        if type(msg).__name__ != 'bytes':
            msg = msg.encode()
        cipher = PKCS1_v1_5.new(RSA.import_key(receiver_key))
        return cipher.encrypt(msg)

    def decrypt_msg(self, msg, is_str=False):

        cipher = PKCS1_v1_5.new(RSA.import_key(self.private_key))
        if is_str:
            return cipher.decrypt(msg, None).decode()
        return cipher.decrypt(msg, None)

    def get_public_key(self):

        return self.public_key


if __name__ == '__main__':
    from classes import asymmetric_encryption

    encryption = asymmetric_encryption.AsymmetricEncryption()
    msg = 'hello'   # limit 245
    msg_encrypted = encryption.encrypt_msg(msg, encryption.get_public_key())
    print('len', len(msg_encrypted))
    msg = encryption.decrypt_msg(msg_encrypted)
    print(msg)