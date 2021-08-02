from os import path

from classes.Player import Player
from config import FILES_DIR
from util import hex_to_str, read_until_null

FILES_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', FILES_DIR, '')

CHARSET = 'utf-8'
BLOCK_LENGTH = 16
POINTERS_START_POS = 0x3288

NATIONAL_PLAYERS_BLOCK_LENGTH = 46
NATIONAL_NUMBERS_BLOCK_LENGTH = 23

CLUB_PLAYERS_BLOCK_LENGTH = 64
CLUB_NUMBERS_BLOCK_LENGTH = 32


class Team:
    id: int
    name: str
    abbr: str
    bytes_sequence: list

    def __str__(self):
        return self.name

    @classmethod
    def from_id(cls, _id: int):
        t = cls()
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
    def from_name(cls, name: str):
        return [t for t in cls.get_all() if name.upper() in t.name.upper()]

    @classmethod
    def get_all(cls):
        return [cls.from_id(x) for x in range(381)]

    def _get_players(self, squad_file: str, numbers_file: str, club: bool, id_reduction: int = 0) -> list:
        players_block_length = CLUB_PLAYERS_BLOCK_LENGTH if club else NATIONAL_PLAYERS_BLOCK_LENGTH
        numbers_block_length = CLUB_NUMBERS_BLOCK_LENGTH if club else NATIONAL_NUMBERS_BLOCK_LENGTH

        with open(FILES_DIRECTORY + squad_file, 'rb') as ID00051_001:
            ID00051_001.seek((self.id - id_reduction) * players_block_length)
            x = ID00051_001.read(players_block_length)

        with open(FILES_DIRECTORY + numbers_file, 'rb') as ID00051_003:
            ID00051_003.seek((self.id - id_reduction) * numbers_block_length)
            y = ID00051_003.read(numbers_block_length)

        IDs = []
        numbers = []
        counter = 0

        while True:
            try:
                _id = x[counter * 2] + x[counter * 2 + 1] * 16 ** 2

                if _id == 0:
                    break

                IDs.append(_id)
                numbers.append(y[counter] + 1)
                counter += 1
            except IndexError:
                break

        players = []
        for number, _id in zip(numbers, IDs):
            player = Player.from_id(_id)
            # player.number = number
            # player.club = self.name
            players.append(player)

        return players


class National(Team):
    @classmethod
    def get_all(cls):
        return [cls.from_id(x) for x in range(67)]

    def get_players(self):
        return super()._get_players('ID00051_001', 'ID00051_003', False)


class Club(Team):
    @classmethod
    def get_all(cls):
        return [cls.from_id(x) for x in range(67, 381)]

    def get_players(self):
        return super()._get_players('ID00051_002', 'ID00051_004', True, 67)
