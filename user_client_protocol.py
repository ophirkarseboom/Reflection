def unpack(data: str):
    """
    parsing by protocol and returns a tuple: (opcode, [params])
    :param data: msg that got from client
    :return: a tuple: (opcode, [params])
    """
    if len(data) < 2:
        return
    opcode = data[:2]
    data = data[2:]

    if opcode == '05':
        parsed = ''
        # handle got file treed TBD
    else:
        parsed = data.split(',')

    return opcode, parsed


def pack_register(username: str, password: str):
    """
    builds message by protocol and returns packed str
    :param username: str
    :param password: str
    :return: packed str
    """
    opcode = '01'
    return f'{opcode}{username},{password}'


def pack_sign_in(username: str, password: str, mac: str):
    """
    builds message by protocol and returns packed str
    :param username: str
    :param password: str
    :param mac: str
    :return: packed str
    """
    opcode = '01'
    return f'{opcode}{username},{password},{mac}'


def pack_do_create(location: str, type: str):
    """
    builds message by protocol and return packed str
    :param location: str
    :param type: str
    :return: packed str
    """
    opcode = '06'
    return f'{opcode}{location},{type}'


def pack_do_rename(location: str, new_name: str):
    """
    builds message by protocol and return packed str
    :param location: str
    :param new_name: str
    :return: packed str
    """
    opcode = '08'
    return f'{opcode}{location},{new_name}'


def pack_do_delete(location: str):
    """
    builds message by protocol and return packed str
    :param location: str
    :return: packed str
    """
    opcode = '10'
    return f'{opcode}{location}'


def pack_do_move(old_location: str, new_location: str):
    """
    builds message by protocol and return packed str
    :param old_location: str
    :param new_location: str
    :return: packed str
    """
    opcode = '12'
    return f'{opcode}{old_location},{new_location}'


def pack_do_clone(old_location: str, new_location: str):
    """
    builds message by protocol and return packed str
    :param old_location: str
    :param new_location: str
    :return: packed str
    """
    opcode = '14'
    return f'{opcode}{old_location},{new_location}'


def pack_do_open_file(location: str):
    """
    builds message by protocol and return packed str
    :param location: str
    :return: packed str
    """
    opcode = '16'
    return f'{opcode}{location}'


def pack_change_file(location: str, data: bytes):
    """
    builds message by protocol and return packed str
    :param data: data of file in binary
    :param location: str
    :return: packed str
    """
    opcode = '18'
    return f'{opcode}{location},{data}'




if __name__ == '__main__':
    path = 'T:\public\יב\ophir\Reflection\עיצוב.docx'
    with open(path, 'rb') as f:
        b = f.read()

    print(pack_change_file(path, b)[0:2])
