from os import path

from config import FILES_DIR
from util import hex_to_str, read_until_null

FILES_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', FILES_DIR, '')

CHARSET = 'utf-8'
BLOCK_LENGTH = 16
POINTERS_START_POS = 0x3288


class Team:
    id: int
    name: str
    abbr: str
    bytes_sequence: list

    @classmethod
    def from_id(cls, _id):
        t = Team()
        t.id = _id

        with open(FILES_DIRECTORY + 'ID00015', 'rb') as ID00015:
            ID00015.seek(POINTERS_START_POS + BLOCK_LENGTH * _id)
            byte_sequence = ID00015.read(BLOCK_LENGTH)

            name_pos = (byte_sequence[1] - 0x18) * 0x100 + byte_sequence[0]
            abbr_pos = (byte_sequence[5] - 0x18) * 0x100 + byte_sequence[4]

            t.bytes_sequence = hex_to_str(byte_sequence)

            ID00015.seek(name_pos)
            t.name = read_until_null(ID00015).decode(CHARSET)

            ID00015.seek(abbr_pos)
            t.abbr = read_until_null(ID00015).decode(CHARSET)

        return t

    @classmethod
    def get_all(cls):
        return [Team.from_id(x) for x in range(381)]


class National(Team):
    @classmethod
    def get_all(cls):
        return [National.from_id(x) for x in range(67)]


class Club(Team):
    @classmethod
    def get_all(cls):
        return [National.from_id(x) for x in range(67, 381)]
