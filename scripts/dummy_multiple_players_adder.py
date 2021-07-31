from os import path

from classes.Player import Player
from config import FILES_DIR, CSV_DIR

FILES_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), FILES_DIR, '')
CSV_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), CSV_DIR, '')

CHARSET = 'utf-8'


def main():
    qty = int(input('Inserisci il numero di giocatori da aggiungere: '))
    player = Player()
    block = player.get_block()

    try:
        with open(FILES_DIRECTORY + 'ID00051_000', 'ab') as f:
            f.write(block * qty)
    except Exception as e:
        print(e.__str__())


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e.__str__())
        input('Premi INVIO per terminare')
