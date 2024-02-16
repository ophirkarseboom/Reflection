import ctypes
import os
from Reflection.settings import Settings


class FileHandler:
    root = Settings.root

    def __init__(self, username: str):
        self.my_ip = Settings.get_ip()
        self.username = username
        self.user_path = self.root + username + '\\'

    def create_root(self):
        """
        creates root directory hidden
        :return:
        """
        FileHandler._create_hidden_dir(self.root)
        FileHandler.create(self.user_path, 'fld')

    def is_local(self, path):
        """
        gets path and returns if local
        :param path: path of dir
        :return: if path is local or not
        """
        return path.startswith(self.user_path + self.my_ip) and os.path.exists(FileHandler.remove_ip(self.username, path))

    @staticmethod
    def split_path_last_part(path):
        """
        gets path and removes last part of it
        :param path: a path
        :return: path updated, last part
        """
        # Split the path into its components
        path_components = path.split(os.path.sep)

        # Get the last component
        last_part = path_components[-1]

        # Remove the last component
        updated_path_components = path_components[:-1]

        # Join the updated components back into a path
        updated_path = os.path.sep.join(updated_path_components)

        return updated_path, last_part

    @staticmethod
    def open_file(path: str):
        """
        gets path and opens file
        :param path: path of file
        """
        os.system('start "" "' + path + '"')


    @staticmethod
    def insert_ip(path: str, username: str, ip: str):
        """
        gets username and path and inserts ip in it
        :param username: username
        :param path: path to insert into
        :param ip: ip to insert
        :return: path with ip in it
        """
        ip_to_insert = '\\' + ip
        return path.replace(username, username + ip_to_insert)


    @staticmethod
    def extract_ip(username: str, path: str):
        """
        gets path and extracts ip out of it
        :param path: path
        :return: ip in path
        """
        ip = None
        if username in path:
            user_path_len = path.index(username) + len(username) + 1
            if user_path_len < len(path):
                ip = path[user_path_len:]
                if '\\' in ip:
                    ip = ip[:ip.index('\\')]

        return ip

    @staticmethod
    def remove_ip(username, path: str):
        """
        gets path and removes ip out of it
        :param path: path
        :return: path without ip
        """
        if username in path:
            user_path_len = path.index(username) + len(username) + 1
            if user_path_len < len(path):
                ip = path[user_path_len:]

                if '\\' in ip:
                    ip = '\\' + ip[:ip.index('\\')]

                if ip in path:
                    print('hi')
                    path = path.replace(ip, '')

        return path

    @staticmethod
    def create(path: str, typ: str):
        """
        gets path to create, creates it if does not exist
        :param path: path to dir
        :param typ: type of creation
        :return: if created or not
        """
        created = True
        if not os.path.exists(path):
            if typ == 'fld':
                os.makedirs(path)
            else:
                with open(f'{path}.{typ}', 'w') as fp:
                    pass
        else:
            created = False

        return created

    @staticmethod
    def _create_hidden_dir(path):
        """
        gets path for dir and creates it hidden
        :param path: path for dir
        :return: None
        """
        FileHandler.create(path, 'fld')
        attrs = os.stat(path).st_file_attributes
        if not attrs & 2 == 2:
            # Get the file attributes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
            # Add the 'hidden' attribute
            ctypes.windll.kernel32.SetFileAttributesW(path, attrs | 2)

    @staticmethod
    def get_user(path: str):
        """
        gets path and returns user inside path
        :param path: a path
        :return: user inside path
        """
        path = path.split(os.path.sep)
        user = None
        if len(path) >= 3:
            user = path[2]
        return user

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
    a = FileHandler('ophir')
    print(a.is_local('T:\public\cyber\ophir\Reflection\Reflection\protocols\server_protocol.py'))