from scripts.util import get_cl_clubs, get_clubs, get_nationalities, get_nationals

charset = 'utf-8'


def main():
    with open('files/ID00015', 'rb') as ID00015:

        nationalities = get_nationalities(ID00015)
        nationals = get_nationals(ID00015)
        clubs = get_clubs(ID00015)

        with open('files/nationalities.csv', 'w+', encoding=charset) as f:
            f.write(
                '\n'.join(
                    ','.join(
                        [k, *nationalities[k].values()]
                    ) for k in nationalities.keys()
                )
            )

        with open('files/nationals.csv', 'w+', encoding=charset) as f:
            f.write(
                '\n'.join(
                    ','.join(
                        [k, *nationals[k].values()]
                    ) for k in nationals.keys()
                )
            )

        with open('files/clubs.csv', 'w+', encoding=charset) as f:
            f.write(
                '\n'.join(
                    ','.join(
                        [k, *clubs[k].values()]
                    ) for k in clubs.keys()
                )
            )

    with open('files/EBOOT.OLD', 'rb') as EBOOT:
        cl_teams = get_cl_clubs(EBOOT)

        for key_1 in cl_teams:
            club = clubs.get(key_1)

            for key_2 in club:
                cl_teams.get(key_1)[key_2] = cl_teams.get(key_1).get(key_2) or club.get(key_2)

        with open('files/champions_league.csv', 'w+', encoding=charset) as f:
            f.write(
                '\n'.join(
                    ','.join(
                        [k, *cl_teams[k].values()]
                    ) for k in cl_teams.keys()
                )
            )


if __name__ == '__main__':
    main()
