import netifaces as ni
from Reflection.file_stuff.file_handler import FileHandler
print(ni.interfaces())
my_ip = ni.ifaddresses(ni.interfaces()[0])[ni.AF_INET][0]['addr']
print(my_ip)
a = FileHandler('ophir', my_ip)
a.create_root()

print(424.5 + 10 + 86 - 12.5 + 150 -150 - 38 - 150 - 200 + 240 - 200 -200 - 90 - 17 - 200 - 9 -15  - 80 - 70 + 150 - 200 - 11- 11 + 26 - 15 + 75 + 9.5 + 128 + 145 - 10 + 60 + 20- 80 - 20 + 60 - 30 + 70 + 25 - 60 + 120 - 50)