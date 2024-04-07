import os
import ast
def unpack(data: str):
    """
    parsing by protocol and returns a tuple: (opcode, [params])
    :param data: msg that got from client
    :return: a tuple: (opcode, [params])
    """
    if len(data) > 1:
        opcode = data[:2]
        data = data[2:]

        # if got file tree
        if opcode == '20':


            parsed = [data]
        else:
            parsed = data.split(',')


        return opcode, parsed



def pack_status_mac(status: bool):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :return: packed str
    """
    packed = '34'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return packed


def pack_status_register(status: bool):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :return: packed str
    """
    packed = '02'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return packed


def pack_status_login(status: bool):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :return: packed str
    """
    packed = '04'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return packed


def pack_status_create(status: bool, path: str, typ: str):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :param path: path of creation
    :param typ: type of creation
    :return: packed str
    """
    packed = '07'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return f'{packed},{path},{typ}'


def pack_status_rename(status: bool, path: str, new_name: str):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :param path: path of file
    :param new_name:
    :return: packed str
    """
    packed = '09'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return f'{packed},{path},{new_name}'


def pack_status_delete(status: bool, location: str):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :param location: location of delete
    :return: packed str
    """
    packed = '11'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return f'{packed},{location}'


def pack_status_move(status: bool, old_path: str, new_path: str):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param status: boolean (success of failure)
    :param old_path: the old path of the file
    :param new_path: new path of the file
    :return: packed str
    """
    packed = '13'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return f'{packed},{old_path},{new_path}'


def pack_status_clone(status: bool, copy_from: str, copy_to: str):
    """
    gets a boolean that tells if action worked or not and returns the packed str
    :param copy_to: folder to copy to
    :param copy_from: path of file to copy
    :param status: boolean (success of failure)
    :return: packed str
    """
    packed = '15'
    if status:
        packed += 'ok'
    else:
        packed += 'no'

    return f'{packed},{copy_from},{copy_to}'


def pack_do_remove(folder: str):
    """
    gets a certain folder and returns packed by protocol that tells to remove it
    :param folder: str
    :return: packed str
    """
    return f'30{folder}'


def pack_ask_file_Tree(folder: str):
    """
    :return: protocol for asking file system
    """
    return f'31{folder}'


def pack_send_file_tree(file_tree: str):

    """
    builds message by protocol and returns packed str
    :param file_tree: the file tree
    :return: packed str
    """
    return f'05{file_tree}'


def pack_do_rename(location: str, new_name: str):
    """
    gets location of file/folder and name to rename to, returns packed str that does it by protocol
    :param location: location of file/folder
    :param new_name: location of file/folder
    :return: packed str
    """
    opcode = '21'
    return f'{opcode}{location},{new_name}'


def pack_do_create(location: str, typ: str):
    """
    gets location of file/folder and type to create, returns packed str that does it by protocol
    :param location: location of file/folder
    :param typ: type of file or folder
    :return: packed str
    """
    opcode = '32'
    return f'{opcode}{location},{typ}'

def pack_do_delete(location: str):
    """
    gets location of file/folder to delete, returns packed str that does it by protocol
    :param location: location of file/folder
    :return: packed str
    """
    opcode = '23'
    return f'{opcode}{location}'


def pack_do_move(old_location: str, new_location: str):
    """
    gets location of file to move and new location to move it, returns packed str that does it by protocol
    :param old_location: location of file
    :param new_location: new location of file
    :return: packed str
    """
    opcode = '25'
    return f'{opcode}{old_location},{new_location}'


def pack_do_clone(old_location: str, new_location: str):
    """
    gets location of file to clone and new location to clone it, returns packed str that does it by protocol
    :param old_location: location of file
    :param new_location: new location of file
    :return: packed str
    """
    opcode = '27'
    return f'{opcode}{old_location},{new_location}'


def pack_public_key(public_key):
    """
    get public key and packs it by protocol
    :param public_key: a public key
    :return: packed str
    """
    return b'98'+public_key

