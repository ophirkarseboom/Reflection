
from Crypto.Random import get_random_bytes
import base64

import Crypto.Util.Padding
from Crypto.Cipher import AES
from Crypto import Random
import hashlib



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
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc, is_image=False):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        if not is_image:
            return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        if type(s).__name__ == 'str':
            s = s.encode()
        return Crypto.Util.Padding.pad(s, 16, style='pkcs7')

    @staticmethod
    def _unpad(s):
        return Crypto.Util.Padding.unpad(s, 16, style='pkcs7')


if __name__ == '__main__':
    encryption = SymmetricalEncryption()
    data = encryption.encrypt_msg('hello')
    print(data)
    data = encryption.decrypt_msg(data)
    print(data)
