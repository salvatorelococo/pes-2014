from os import path

from classes.Team import Club
from config import FILES_DIR, CSV_DIR
from util import get_cl_clubs

FILES_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', FILES_DIR, '')
CSV_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', CSV_DIR, '')

CHARSET = 'utf-8'


def main():
    with open(FILES_DIRECTORY + 'EBOOT.OLD', 'rb') as f:
        cl_teams = get_cl_clubs(f)

    for cl_team in cl_teams:
        club = Club.from_id(cl_team['id'])
        cl_team['abbr'] = club.abbr
        cl_team['name'] = club.name

    with open(CSV_DIRECTORY + 'champions_league.csv', 'w+', encoding=CHARSET) as f:
        f.write('\n'.join(','.join([str(x) for x in cl_team.values()]) for cl_team in cl_teams))


if __name__ == '__main__':
    main()
