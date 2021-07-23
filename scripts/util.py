from typing import BinaryIO

from scripts.names_structure import pointers

CHARSET = 'utf-8'


def get_cl_clubs(stream: BinaryIO):
    clubs = {}
    offset = 0x2C3358

    stream.seek(offset)

    while True:
        seq = stream.read(8)

        # TODO: Will it be always true?
        if seq[1] != 0x01:
            break

        _id = seq[4]
        clubs[normalize_id(_id)] = {
            'hex_seq': hex_to_str(seq)
        }

    return clubs


def get_nationalities(stream: BinaryIO):
    nationalities = {}

    _id = 0
    _length = 8

    n = pointers.get('nationalities')
    start_offset = n.get('start')
    end_offset = n.get('end')
    stream.seek(start_offset)

    while True:
        offset = start_offset + _id * _length

        if offset >= end_offset:
            break

        nationalities[normalize_id(_id)] = get_data(stream, offset, _length)

        _id += 1

    return nationalities


def get_nationals(stream: BinaryIO):
    nationals = {}

    _id = 0
    _length = 16

    # TODO: Improve structure
    n = pointers.get('nationals')
    start_offset = n.get('europe_a').get('start')
    end_offset = n.get('classics').get('end')

    stream.seek(start_offset)

    while True:
        offset = start_offset + _id * _length

        if offset >= end_offset:
            break

        nationals[normalize_id(_id)] = get_data(stream, offset, _length)

        _id += 1

    return nationals


def get_clubs(stream: BinaryIO):
    clubs = {}

    _id = 0
    _length = 16

    # TODO: Improve structure
    c = pointers.get('clubs')
    start_offset = c.get('premier_league').get('start')
    end_offset = c.get('unknown_clubs').get('end')

    stream.seek(start_offset)

    while True:
        offset = start_offset + _id * _length

        if offset >= end_offset:
            break

        clubs[normalize_id(_id + 67)] = get_data(stream, offset, _length)

        _id += 1

    return clubs


def get_data(stream: BinaryIO, offset, _length):
    stream.seek(offset)
    info = stream.read(_length)

    name_pos = (info[1] - 0x18) * 0x100 + info[0]
    abbr_pos = (info[5] - 0x18) * 0x100 + info[4]

    stream.seek(name_pos)
    name = read_until_null(stream)

    stream.seek(abbr_pos)
    abbr = read_until_null(stream)

    return {
        'hex_seq': hex_to_str(info),
        'abbr': abbr.decode(CHARSET),
        'name': name.decode(CHARSET)
    }


def hex_to_str(stream: bytes) -> str:
    return ' '.join(hex(b)[2:].upper().zfill(2) for b in stream)


def normalize_id(_id: int):
    _id = hex(_id)[2:].upper()

    if not len(_id) % 2:
        return _id
    else:
        return '0' + _id


def read_until_null(stream: BinaryIO):
    s = b''
    while True:
        c = stream.read(1)

        if c == b'\x00':
            break

        s += c

    return s


def list_to_hex(int_list: list):
    hex_str = b''

    for val in int_list:
        hex_str += chr(val).encode('iso-8859-1')

    return hex_str
