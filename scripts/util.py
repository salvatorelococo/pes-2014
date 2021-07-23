import csv
from typing import BinaryIO

from names_structure import pointers

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
        clubs[_id] = {
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

        nationalities[_id] = get_data(stream, offset, _length)

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

        nationals[_id] = get_data(stream, offset, _length)

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

        clubs[_id + 67] = get_data(stream, offset, _length)

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


def list_to_bytes(int_list: list):
    hex_str = b''

    try:
        for val in int_list:
            hex_str += chr(val).encode('iso-8859-1')
    except UnicodeEncodeError as e:
        print(len(hex_str))
        raise e

    return hex_str


def get_nationality_id(s: str):
    with open('files/ID00015', 'rb') as ID00015:
        nationalities = get_nationalities(ID00015)

        for k in nationalities.keys():
            if s.upper() == nationalities[k]['name']:
                return int(k)

        print('Nazionalità non trovata!', end=' ')
        while True:
            try:
                _id = int(input('Inserisci l\'ID della nazionalità (valore decimale): '))
                print()

                if _id in nationalities.keys():
                    print('Nazionalità selezionata: ', nationalities[_id])
                    print()

                    while True:
                        x = input('Confermare? (s/n): ').lower()

                        if x in ['s', 'n']:
                            break

                    if x == 'n':
                        continue

                    return _id
            except ValueError:
                pass


def get_players():
    block_length = 0x7C
    charset = 'utf-16'

    players = {}

    with open('files/ID00051_000', 'rb') as ID00015:
        _id = 1

        while True:
            ID00015.seek(block_length * _id)

            block = ID00015.read(block_length)
            if block == b'':
                break

            name = block[:32]
            name = name.replace(b'\x00\x00', b'')

            players[_id] = {'name': name.decode(charset), 'block': block}
            _id += 1

    return players


def get_players_by_name(s: str):
    s = s.upper()
    players = get_players()

    res = []

    for k in players.keys():
        if players[k]['name'].upper() in s:
            res.append({'id': k, 'name': players[k]['name'], 'block': players[k]['block']})

    return res
