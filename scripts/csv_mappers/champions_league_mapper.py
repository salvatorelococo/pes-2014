from util import get_clubs, get_cl_clubs

CHARSET = 'utf-8'


def main():
    with open('../files/ID00015', 'rb') as f:
        clubs = get_clubs(f)

    with open('../files/EBOOT.OLD', 'rb') as f:
        cl_teams = get_cl_clubs(f)

    for key_1 in cl_teams:
        club = clubs.get(key_1)

        for key_2 in club:
            cl_teams.get(key_1)[key_2] = cl_teams.get(key_1).get(key_2) or club.get(key_2)

    with open('../csv/champions_league.csv', 'w+', encoding=CHARSET) as f:
        f.write(
            '\n'.join(
                ','.join(
                    [str(k), *cl_teams[k].values()]
                ) for k in cl_teams.keys()
            )
        )


if __name__ == '__main__':
    main()
