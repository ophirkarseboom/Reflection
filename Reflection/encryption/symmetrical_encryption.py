
import base64
import hashlib

import Crypto.Util.Padding
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class SymmetricalEncryption:
    p = 9413
    g = 757

    def __init__(self, key=None):

        if not key:
            self.key = get_random_bytes(32)
        else:
            self.key = key
        self.encryption = hashlib.sha256(self.key).digest()

    def encrypt(self, raw):
        """
        gets data and returns it encrypted
        :param raw: data
        :return: encrypted data
        """
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc, is_image=False):
        """
        gets encrypted data and returns it decrypted
        :param enc: data encrypted
        :param is_image: if the data is image or not
        :return: data decrypted
        """
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_msg = self._unpad(cipher.decrypt(enc[AES.block_size:]))
        if not is_image:
            decrypted_msg = decrypted_msg.decode('utf-8')

        return decrypted_msg

    def _pad(self, s):
        """
        gets data and pads it
        :param s: data
        :return: data with pad
        """
        if type(s).__name__ == 'str':
            s = s.encode()
        return Crypto.Util.Padding.pad(s, 16, style='pkcs7')

    @staticmethod
    def _unpad(s):
        """
        gets data pad returns it without pad
        :param s: data
        :return: data without pad
        """
        return Crypto.Util.Padding.unpad(s, 16, style='pkcs7')

    @staticmethod
    def hash(data):
        """
        gets data and hashes it
        :param data: data
        :return: data hashed
        """
        data = bytes(str(data), 'utf-8')
        return hashlib.sha256(data).digest()


if __name__ == '__main__':
    encryption = SymmetricalEncryption()
    data = encryption.encrypt('hello')
    print(data)
    data = encryption.decrypt(data)
    print(data)
