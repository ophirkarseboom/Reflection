from Reflection.local_handler.file_handler import FileHandler

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
    opcode = '20'
    return f'{opcode}{FileHandler.get_path_tree(path)}'

def pack_mac(mac: str):
    """
    builds message by protocol and returns packed str
    :param mac: mac address
    :return: packed str
    """
    opcode = '29'
    return f'{opcode}{mac}'


def pack_status_create(status: bool, location: str, typ: str):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :param location: location of creation
    :param typ: type of creation
    :return: packed str
    """
    packed = '33'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return f'{packed},{location},{typ}'


def pack_status_rename(status: bool, location: str, new_name: str):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :param location: location of renaming
    :param new_name: new name of file\folder
    :return: packed str
    """
    packed = '22'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return f'{packed},{location},{new_name}'


def pack_status_delete(status: bool, location: str):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :param location: location of delete
    :return: packed str
    """
    packed = '24'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return f'{packed},{location}'


def pack_status_move_to_server(status: bool, old_path: str, new_path: str):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :param old_path: the old path of the file
    :param new_path: the new path of the file
    :return: packed str
    """
    packed = '26'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return f'{packed},{old_path},{new_path}'

def pack_do_move(new_path: str, old_path: str):
    """
    builds by protocol to move file
    :param new_path: the path of the file to save it with
    :param old_path: the old path of the file
    :return: packed str
    """
    packed = '38'
    return f'{packed}{new_path},{old_path}'


def pack_status_move_to_client(status: bool, moved_to: str, moved_from: str):
    """
    packs if worked moving file to client
    :param status: boolean (success of failure)
    :param moved_to: the new path of the file
    :param moved_from: the old path of the file
    :return: packed str
    """
    packed = '39'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return f'{packed},{moved_to},{moved_from}'


def pack_do_clone(new_path: str, old_path: str):
    """
    builds by protocol to clone file
    :param new_path: the path of the file to save it with
    :param old_path: the old path of the file
    :return: packed str
    """
    packed = '36'
    return f'{packed}{new_path},{old_path}'


def pack_status_clone_to_client(status: bool, cloned_to: str, cloned_from: str):
    """
    packs if worked cloning file to client
    :param status: boolean (success of failure)
    :param cloned_to: the new path of the file
    :param cloned_from: the old path of the file
    :return: packed str
    """
    packed = '37'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return f'{packed},{cloned_to},{cloned_from}'

def pack_status_clone_to_server(status: bool, copy_from: str, copy_to: str):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param copy_to: folder to copy to
    :param copy_from: path to copy from
    :param status: boolean (success of failure)
    :return: packed str
    """
    packed = '28'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return f'{packed},{copy_from},{copy_to}'


def pack_status_open_file(status: bool, path=''):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param path: path of file if able to open file
    :param status: boolean (success of failure)
    :return: packed str
    """
    packed = '17'
    if status:
        packed += f'ok,{path}'
    else:
        packed += 'no'

    return packed


def pack_status_change_file(status: bool, path: str):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :param path: path of the file changed
    :return: packed str
    """
    packed = '19'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return f'{packed},{path}'


def pack_key(key):
    """
    builds by protocol to send symmetrical key
    :param key: a symmetrical key
    :return: packed str
    """
    return b'99'+key
