import ctypes
import os
from Reflection.settings import Settings


class FileHandler:
    root = Settings.root

    def __init__(self, username: str, ip: str):

        self.user_path = self.root + username + '\\'
        self.ip = ip

    def create_root(self):
        """
        creates root directory hidden
        :return:
        """
        FileHandler._create_hidden_dir(self.root)
        FileHandler.create_dir(self.user_path)
        FileHandler.create_dir(f"{self.user_path}{self.ip}")

    def is_local(self, path):
        """
        gets path and returns if local
        :param path: path of dir
        :return: if path is local or not
        """
        return path.startswith(self.user_path) and os.path.exists(path)


    @staticmethod
    def _create_hidden_dir(path):
        """
        gets path for dir and creates it hidden
        :param path: path for dir
        :return: None
        """
        FileHandler.create_dir(path)
        attrs = os.stat(path).st_file_attributes
        if not attrs & 2 == 2:
            # Get the file attributes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
            # Add the 'hidden' attribute
            ctypes.windll.kernel32.SetFileAttributesW(path, attrs | 2)


    @staticmethod
    def create_dir(path):
        """
        gets path to directory, creates it if does not exist
        :param path: path to dir
        :return: None
        """
        if not os.path.exists(path):
            os.mkdir(path)

    @staticmethod
    def get_path_tree(path: str):
        """
        returns path to dir returns tree of dir
        :param path: path to dir
        :return: file tree of path
        """
        file_tree = ''
        for part in os.walk(path):
            part = f'{part[0]}?{part[1]}?{part[2]}\n'
            file_tree += part

        return file_tree


if __name__ == '__main__':
    a = FileHandler('ophir', '192.168.4.82')
    print(a.is_local('T:\public\cyber\ophir\Reflection\Reflection\protocols\server_protocol.py'))