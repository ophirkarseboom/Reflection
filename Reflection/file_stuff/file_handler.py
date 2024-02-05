import ctypes
import os


class FileHandler:
    root = 'D:\\reflection\\'

    def __init__(self, username: str, ip: str):

        self.username = username
        self.ip = ip

    def create_root(self):
        FileHandler._create_hidden(self.root)
        FileHandler._create_hidden(self.root + self.username)
        FileHandler._create_hidden(self.root + self.username + self.ip)

    @staticmethod
    def _create_hidden(path):
        if not os.path.exists(path):
            os.mkdir(path)
        attrs = os.stat(path).st_file_attributes
        if not attrs & 2 == 2:
            # Get the file attributes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
            # Add the 'hidden' attribute
            ctypes.windll.kernel32.SetFileAttributesW(path, attrs | 2)


