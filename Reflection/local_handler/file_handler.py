import ctypes
import os
from Reflection.settings import Settings
import shutil
from subprocess import Popen

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


    @ staticmethod
    def split_name_typ(name: str):
        """
        splits name and type
        :param name: name of file
        :return: name parted (name, type)
        """
        typ_index = name.rfind('.')
        typ = name[typ_index + 1:]
        name = name[:typ_index]
        return name, typ

    @ staticmethod
    def build_name_for_file(file_tree: dict, new_dir_path: str, path_of_file: str, adding: str):
        """
        building a name to a file to fit to directory
        :param file_tree: the file tree using
        :param new_dir_path: path of new folder
        :param path_of_file: path of a file to build name for
        :param adding: adding at end of file for new name
        :return: new name of the file
        """
        _, file_name = FileHandler.split_path_last_part(path_of_file)
        new_file_name = file_name
        if file_name in file_tree[new_dir_path]:
            if adding not in file_name:
                parted_file_name = file_name.split('.')
                parted_file_name[0] += adding
                new_file_name = '.'.join(parted_file_name)

            # adding count numbers if copied several times
            count = 1
            while True:
                if new_file_name in file_tree[new_dir_path]:
                    parted_file_name = new_file_name.split('.')
                    parted_file_name[0] = parted_file_name[0].split('-')[0] + f'-{count}'
                    new_file_name = '.'.join(parted_file_name)
                    count += 1
                else:
                    break

        return new_file_name

    @ staticmethod
    def direct_copy_file(from_path: str, to: str):
        """
        copies a file
        :param from_path: original path
        :param to: new path
        :return: if was able to copy file
        """
        worked = os.path.isfile(from_path)
        print('file_path:', from_path)
        if worked:
            shutil.copy(from_path, to)
        return worked

    @ staticmethod
    def move(old_path: str, new_path: str):
        """
        moves a file
        :param old_path: old path of file
        :param new_path: the new path of the file
        :return: if success in moving file
        """
        worked = os.path.isfile(old_path)
        if worked:
            shutil.move(old_path, new_path)
        return worked



    @ staticmethod
    def rename(location: str, new_name: str):
        """
        gets path and renames it
        :param location: path to rename
        :param new_name: new name to rename to
        :return: if renamed or not
        """
        rename = False
        new_path, _ = FileHandler.split_path_last_part(location)
        new_path += f'\\{new_name}'
        print('new_path:', new_path)
        if os.path.exists(location) and not os.path.exists(new_path):
            try:
                os.rename(location, new_path)
            except Exception:
                rename = False
            else:
                rename = True

        return rename


    @staticmethod
    def delete(location: str):
        """
        gets path and deletes it from computer
        :param location: path to delete
        """
        delete = False
        if os.path.isdir(location):
            delete = True
            shutil.rmtree(location)
        elif os.path.isfile(location):
            delete = True
            os.remove(location)

        return delete

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
        Popen(['start', path], shell=True)


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
        return path.replace(username, username + ip_to_insert, 1)


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
        :param username: username of user
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
                    path = path.replace(ip, '', 1)

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