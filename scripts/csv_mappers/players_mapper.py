from os import path

from classes.Player import Player
from config import FILES_DIR, CSV_DIR
from util import hex_to_str

FILES_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', FILES_DIR, '')
CSV_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', CSV_DIR, '')

BLOCK_LENGTH = 0x7C
CHARSET = 'utf-16'


def main():
    players = Player.get_all()

    with open(CSV_DIRECTORY + 'players.csv', 'w+', encoding=CHARSET) as o:
        for p in players:
            o.write(f'{p.id},{p.name},{hex_to_str(p.get_block())}\n')


if __name__ == '__main__':
    main()
