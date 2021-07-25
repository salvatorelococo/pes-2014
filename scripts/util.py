from typing import BinaryIO

from files_structure.ID00015_structure import pointers

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
            'abbr': '',
            'name': '',
            'group': '',
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

    n = pointers.get('nationals')

    for k in n:
        _id_k = 0
        group = n[k].get('title')
        start_offset = n[k].get('start')
        end_offset = n[k].get('end')

        stream.seek(start_offset)

        while True:
            offset = start_offset + _id_k * _length

            if offset >= end_offset:
                break

            nationals[_id] = get_data(stream, offset, _length)
            nationals[_id]['group'] = group

            _id += 1
            _id_k += 1

    return nationals


def get_clubs(stream: BinaryIO):
    clubs = {}

    _id = 67
    _length = 16

    c = pointers.get('clubs')

    for k in c:
        _id_k = 0
        group = c[k].get('title')
        start_offset = c[k].get('start')
        end_offset = c[k].get('end')

        stream.seek(start_offset)

        while True:
            offset = start_offset + _id_k * _length

            if offset >= end_offset:
                break

            clubs[_id] = get_data(stream, offset, _length)
            clubs[_id]['group'] = group

            _id_k += 1
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
        'abbr': abbr.decode(CHARSET),
        'name': name.decode(CHARSET),
        'group': '',
        'hex_seq': hex_to_str(info),
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


def hex_string_to_list(s: str):
    res = []
    s = s.replace(' ', '')

    counter = 0
    while True:
        tmp = s[counter * 2:(counter + 1) * 2]

        if len(tmp) == 0:
            break

        if len(tmp) == 1:
            raise Exception('Invalid hex sequence')

        res.append(int(tmp, 16))
        counter += 1


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


def get_players(stream: BinaryIO):
    block_length = 0x7C
    charset = 'utf-16'

    players = {}
    _id = 1

    while True:
        stream.seek(block_length * _id)

        block = stream.read(block_length)
        if block == b'':
            break

        name = block[:32]
        name = name.replace(b'\x00\x00', b'')

        players[_id] = {'name': name.decode(charset), 'block': hex_to_str(block)}
        _id += 1

    return players


def get_players_by_name(s: str, stream: BinaryIO):
    s = s.upper()
    players = get_players(stream)

    res = []

    for k in players.keys():
        if players[k]['name'].upper() in s:
            res.append({'id': k, 'name': players[k]['name'], 'block': players[k]['block']})

    return res
