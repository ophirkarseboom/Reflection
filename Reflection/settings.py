import netifaces as ni
from uuid import getnode

class Settings:
    server_ip = '10.100.102.27'
    server_port = 2000
    root = 'C:\\reflection\\'




    @staticmethod
    def get_mac_address():
        """ returns  mac address"""
        return ':'.join(['{:02x}'.format((getnode() >> i) & 0xff) for i in range(0, 8 * 6, 8)][::-1])

    @staticmethod
    def get_my_ip():
        """
        :return: computer's ip
        """
        return ni.ifaddresses(ni.interfaces()[1])[ni.AF_INET][0]['addr']

if __name__ == '__main__':
    print(Settings.server_ip)


