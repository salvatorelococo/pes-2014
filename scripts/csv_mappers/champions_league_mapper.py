from util import get_clubs, get_cl_clubs

CHARSET = 'utf-8'


def main():
    with open('../files/ID00015', 'rb') as f:
        clubs = get_clubs(f)

    with open('../files/EBOOT.OLD', 'rb') as f:
        cl_teams = get_cl_clubs(f)

    for cl_team in cl_teams:
        club = clubs.get(cl_team['id'])

        for key_2 in club:
            cl_team[key_2] = cl_team.get(key_2) or club.get(key_2)

    with open('../csv/champions_league.csv', 'w+', encoding=CHARSET) as f:
        f.write(
            '\n'.join(
                ','.join(
                    [str(x) for x in cl_team.values()]
                ) for cl_team in cl_teams
            )
        )


if __name__ == '__main__':
    main()
