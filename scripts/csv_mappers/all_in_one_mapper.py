from scripts.util import get_cl_clubs, get_clubs, get_nationalities, get_nationals, get_players

charset = 'utf-8'


def main():
    # Nationalities
    # Nationals
    # Clubs
    with open('../files/ID00015', 'rb') as ID00015:

        nationalities = get_nationalities(ID00015)
        nationals = get_nationals(ID00015)
        clubs = get_clubs(ID00015)

        with open('../csv/nationalities.csv', 'w+', encoding=charset) as f:
            f.write(
                '\n'.join(
                    ','.join(
                        [str(k), *nationalities[k].values()]
                    ) for k in nationalities.keys()
                )
            )

        with open('../csv/nationals.csv', 'w+', encoding=charset) as f:
            f.write(
                '\n'.join(
                    ','.join(
                        [str(k), *nationals[k].values()]
                    ) for k in nationals.keys()
                )
            )

        with open('../csv/clubs.csv', 'w+', encoding=charset) as f:
            f.write(
                '\n'.join(
                    ','.join(
                        [str(k), *clubs[k].values()]
                    ) for k in clubs.keys()
                )
            )

    # Champions League - Require Clubs
    with open('../files/EBOOT.OLD', 'rb') as EBOOT:
        cl_teams = get_cl_clubs(EBOOT)

        for cl_team in cl_teams:
            club = clubs.get(cl_team['id'])

            for key_2 in club:
                cl_team[key_2] = cl_team.get(key_2) or club.get(key_2)

        with open('../csv/champions_league.csv', 'w+', encoding=charset) as f:
            f.write(
                '\n'.join(
                    ','.join(
                        [str(x) for x in cl_team.values()]
                    ) for cl_team in cl_teams
                )
            )

    # Players
    with open('../files/ID00051_000', 'rb') as ID00051_000:
        players = get_players(ID00051_000)

        with open('../csv/players.csv', 'w+', encoding=charset) as f:
            f.write(
                '\n'.join(
                    ','.join(
                        [str(k), *players[k].values()]
                    ) for k in players.keys()
                )
            )


if __name__ == '__main__':
    main()
