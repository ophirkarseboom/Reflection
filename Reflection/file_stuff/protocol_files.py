import os
import ast
import sys
import time
from collections import deque


def print_nice(text, color):
    bold = '1m'
    red = '91m'
    blue = '94m'
    if color == 'red':
        color = red
    elif color == 'bold':
        color = bold
    elif color == 'blue':
        color = blue
    else:
        color = '0m'
    bold_text = f"\033[{color}" + text + "\033[0m"
    print(bold_text, end='\t')


def print_directory(fold):
    print_nice(fold, 'red')
    bold = True
    count = 0
    for obj in folders[fold]:
        if obj == ',':
            bold = False
        else:
            obj = "{:<40}".format(obj)
            count += 1
            if bold:
                print_nice(obj, 'bold')
            else:
                print(obj, end='\t')
            if count == 4:
                print()
                count = 0




# server side
to_send = ''
while True:
    cwd = input('enter directory to be in: ')
    if os.path.isdir(cwd):
        break
    print('the input is not a directory')

for a in os.walk(cwd):
    a = f'{a[0]}?{a[1]}?{a[2]}\n'
    to_send += a


#client side
folders = {}
lines = to_send.split('\n')[:-1]
for line in lines:
    sep_line = line.split('?')
    directory = sep_line[0]

    dirs = ast.literal_eval(sep_line[1])
    files = ast.literal_eval(sep_line[2])
    dirs.append(',')
    dirs.extend(files)
    folders[directory] = dirs

print(folders)

last_dir = deque()
cwd = list(folders.keys())[0]
while True:
    print_directory(cwd)
    print()
    print_nice('enter something to do: ', 'blue')
    to_do = input()
    if cwd.endswith('\\'):
        path = fr'{cwd}{to_do}'
    else:
        path = f'{cwd}\\{to_do}'

    print('path:', path)
    if to_do == 'exit':
        break
    elif path in folders.keys():
        last_dir.append(cwd)
        cwd = path
    elif to_do == 'back':
        if len(last_dir) == 0:
            print_nice("this is root directory, you can't got back", 'red')
            print()
        else:
            cwd = last_dir.pop()

    else:
        print_nice('wrong input try again', 'red')
        os.system('cls')
        print()


