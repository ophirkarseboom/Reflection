from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


class AsymmetricEncryption:

    def __init__(self, private_key=None, public_key=None):

        if not private_key and not public_key:
            print('0')
            key = RSA.generate(2048)
            print('1')
            self.public_key = key.publickey().export_key()
            print('2')
            self.private_key = key.export_key()
            print('3')
        elif not private_key or not public_key:
            self.private_key = private_key
            self.public_key = public_key
        else:
            raise ValueError('Either provide two arguments or none')

    def encrypt_msg(self, msg, receiver_key):
        """
        gets a msg and a public key
        :param msg: msg to encrypt
        :param receiver_key: key to encrypt with
        :return: encrypted msg
        """
        if type(msg).__name__ != 'bytes':
            msg = msg.encode()
        cipher = PKCS1_v1_5.new(RSA.import_key(receiver_key))
        return cipher.encrypt(msg)

    def decrypt_msg(self, msg, is_str=False):
        """
        gets an encrypted msg and if msg is a string
        :param msg:
        :param is_str:
        :return:
        """
        cipher = PKCS1_v1_5.new(RSA.import_key(self.private_key))
        decrypted_msg = cipher.decrypt(msg, None)
        if is_str:
            decrypted_msg = decrypted_msg.decode()

        return decrypted_msg


    def get_public_key(self):
        """
        returns public key
        :return: public key
        """
        return self.public_key


if __name__ == '__main__':
    from encryption import asymmetric_encryption

    encryption = asymmetric_encryption.AsymmetricEncryption()
    msg = 'hello'   # limit 245
    msg_encrypted = encryption.encrypt_msg(msg, encryption.get_public_key())
    print('len', len(msg_encrypted))
    msg = encryption.decrypt_msg(msg_encrypted)
    print(msg)