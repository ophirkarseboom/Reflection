
from uuid import getnode
import socket
import os

class Settings:
    server_ip = '192.168.4.94'
    server_port = 2000
    root = 'D:\\reflection\\'
    pear_port = 2500
    dir_working_on = os.path.dirname(os.path.realpath(__file__))
    local_path_directory = 'localChange\\'
    local_changes_path = f'{root}{local_path_directory}'
    pic_path = os.path.join(dir_working_on, 'graphics\\icons\\')
    icon_path = pic_path + 'icon_black.png'
    @staticmethod
    def get_ip():
        """
        returns ip
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    @staticmethod
    def get_mac_address():
        """ returns  mac address"""
        return ':'.join(['{:02x}'.format((getnode() >> i) & 0xff) for i in range(0, 8 * 6, 8)][::-1])


if __name__ == '__main__':
    print(Settings.server_ip)


