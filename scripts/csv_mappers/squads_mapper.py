from os import path

from config import FILES_DIR, CSV_DIR
from util import get_clubs, get_nationals, get_players_by_team_id, get_player_by_id

FILES_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', FILES_DIR, '')
CSV_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', CSV_DIR, '')

MAX_NATIONAL_PLAYERS = 23
MAX_CLUB_PLAYERS = 32
CLUB_ID_OFFSET = 67


def main():
    ID00015 = open(FILES_DIRECTORY + 'ID00015', 'rb')          # Teams
    ID00051_000 = open(FILES_DIRECTORY + 'ID00051_000', 'rb')  # Players
    ID00051_001 = open(FILES_DIRECTORY + 'ID00051_001', 'rb')  # Nationals - Squad
    ID00051_002 = open(FILES_DIRECTORY + 'ID00051_002', 'rb')  # Clubs - Squad
    ID00051_003 = open(FILES_DIRECTORY + 'ID00051_003', 'rb')  # Nationals - Shirt numbers
    ID00051_004 = open(FILES_DIRECTORY + 'ID00051_004', 'rb')  # Clubs - Shirt numbers

    nationals = get_nationals(ID00015)
    clubs = get_clubs(ID00015)

    for _id in nationals.keys():
        players = get_players_by_team_id(ID00051_001, _id, MAX_NATIONAL_PLAYERS)

        for p in players:
            p['hex'] = get_player_by_id(ID00051_000, p['id'])

        nationals[_id]['players'] = players
        print(nationals)
        exit()

    for _id in clubs.keys():
        players = get_players_by_team_id(ID00051_002, _id - CLUB_ID_OFFSET, MAX_CLUB_PLAYERS)

        for p in players:
            p['hex'] = get_player_by_id(ID00051_000, p['id'])

        clubs[_id]['players'] = players


if __name__ == '__main__':
    main()
