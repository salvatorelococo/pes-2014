from os import path

from classes.Nationality import Nationality
from classes.Player import Player
from classes.Team import National, Club
from config import FILES_DIR, CSV_DIR
from scripts.util import get_cl_clubs, hex_to_str

FILES_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', FILES_DIR, '')
CSV_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', CSV_DIR, '')

CHARSET = 'utf-8'


def main():
    print('Scansione nazionalità...')
    nationalities = Nationality.get_all()
    with open(CSV_DIRECTORY + 'nationalities.csv', 'w+', encoding=CHARSET) as f:
        f.write('\n'.join(f'{n.id},{n.abbr},{n.name},{n.bytes_sequence}' for n in nationalities))
    print('Scansione nazionalità terminata.\n')

    print('Scansione nazioni...')
    nationals = National.get_all()
    with open(CSV_DIRECTORY + 'nationals.csv', 'w+', encoding=CHARSET) as f:
        f.write('\n'.join(f'{n.id},{n.abbr},{n.name},{n.bytes_sequence}' for n in nationals))
    print('Scansione nazioni terminata.\n')

    print('Scansione club...')
    clubs = Club.get_all()
    with open(CSV_DIRECTORY + 'clubs.csv', 'w+', encoding=CHARSET) as f:
        f.write('\n'.join(f'{c.id},{c.abbr},{c.name},{c.bytes_sequence}' for c in clubs))
    print('Scansione club terminata.\n')

    print('Scansione UEFA Champions League...')
    with open(FILES_DIRECTORY + 'EBOOT.OLD', 'rb') as EBOOT:
        cl_teams = get_cl_clubs(EBOOT)

        for cl_team in cl_teams:
            club = Club.from_id(cl_team['id'])
            cl_team['abbr'] = club.abbr
            cl_team['name'] = club.name

        with open(CSV_DIRECTORY + 'champions_league.csv', 'w+', encoding=CHARSET) as f:
            f.write('\n'.join(','.join([str(x) for x in cl_team.values()]) for cl_team in cl_teams))
    print('Scansione UEFA Champions League terminata.\n')

    print('Scansione giocatori...')
    players = Player.get_all()
    with open(CSV_DIRECTORY + 'players.csv', 'w+', encoding=CHARSET) as f:
        f.write('\n'.join(f'{p.id},{p.name},{hex_to_str(p.get_block())}' for p in players))
    print('Scansione giocatori terminata.\n')


if __name__ == '__main__':
    main()
