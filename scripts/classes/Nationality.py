from os import path

from config import FILES_DIR
from util import read_until_null, hex_to_str

FILES_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', FILES_DIR, '')

CHARSET = 'utf-8'
BLOCK_LENGTH = 8
POINTERS_START_POS = 0xD08
FREE_NATION = 0x64


class Nationality:
    id: int = FREE_NATION
    name: str
    abbr: str
    bytes_sequence: bytes

    @classmethod
    def from_id(cls, _id: int):
        n = Nationality()
        n.id = _id

        with open(FILES_DIRECTORY + 'ID00015', 'rb') as ID00015:
            ID00015.seek(POINTERS_START_POS + BLOCK_LENGTH * _id)
            byte_sequence = ID00015.read(BLOCK_LENGTH)

            name_pos = (byte_sequence[1] - 0x18) * 0x100 + byte_sequence[0]
            abbr_pos = (byte_sequence[5] - 0x18) * 0x100 + byte_sequence[4]

            n.bytes_sequence = hex_to_str(byte_sequence)

            ID00015.seek(name_pos)
            n.name = read_until_null(ID00015).decode(CHARSET)

            ID00015.seek(abbr_pos)
            n.abbr = read_until_null(ID00015).decode(CHARSET)

        return n

    @classmethod
    def get_all(cls):
        return [Nationality.from_id(x) for x in range(143)]

    @classmethod
    def from_name(cls, name: str) -> list:
        return [x for x in Nationality.get_all() if name.upper() in x.name.upper()]

    @classmethod
    def from_abbr(cls, abbr: str):
        res = [x for x in Nationality.get_all() if abbr.upper() == x.abbr.upper()]

        if len(res) == 0:
            return None

        if len(res) == 1:
            return res[0]

        print()

        print(f'Sono stati trovati {len(res)} risultati per {abbr}:')
        for i in range(len(res)):
            print(f'{i:3} | {res[i].name}')

        print()

        while True:
            try:
                x = int(input('Digita il valore corrispondente alla nazionale da selezionare (-1 per annullare): '))

                if x == -1:
                    return None
                if -1 < x < len(res):
                    return res[x]
            except ValueError:
                pass
