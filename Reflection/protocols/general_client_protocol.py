import os

def unpack(data: str):
    """
    parsing by protocol and returns a tuple: (opcode, [params])
    :param data: msg that got from client
    :return: a tuple: (opcode, [params])
    """
    if len(data) > 1:

        opcode = data[:2]
        data = data[2:]

        parsed = data.split(',')

        return opcode, parsed


def pack_client_type(client_type: str):
    """
    builds message by protocol and returns packed str
    :param client_type: the client type
    :return: packed str
    """
    return f'35{client_type}'

def pack_file_tree(path: str):

    """
    builds message by protocol and returns packed str
    :param path: location
    :return: packed str
    """
    packed = '20'
    for part in os.walk(path):
        part = f'{part[0]}?{part[1]}?{part[2]}\n'
        packed += part

    return packed
def pack_mac(mac: str):
    """
    builds message by protocol and returns packed str
    :param mac: mac address
    :return: packed str
    """
    opcode = '29'
    return f'{opcode}{mac}'


def pack_status_create(status: bool):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :return: packed str
    """
    packed = '33'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return packed


def pack_status_rename(status: bool):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :return: packed str
    """
    packed = '22'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return packed


def pack_status_delete(status: bool):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :return: packed str
    """
    packed = '24'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return packed


def pack_status_move(status: bool):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :return: packed str
    """
    packed = '26'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return packed


def pack_status_clone(status: bool):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :return: packed str
    """
    packed = '28'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return packed


def pack_status_open_file(status: bool):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :return: packed str
    """
    packed = '17'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return packed


def pack_status_change_file(status: bool):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :return: packed str
    """
    packed = '19'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return packed


def pack_key(key):
    """
    builds by protocol to send symmetrical key
    :param key: a symmetrical key
    :return: packed str
    """
    return b'99'+key
