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

    parsed = data.split(',')

    return opcode, parsed


def pack_mac(mac: str):
    """
    builds message by protocol and returns packed str
    :param mac: str
    :return: packed str
    """
    opcode = '29'
    return f'{opcode}{}'
