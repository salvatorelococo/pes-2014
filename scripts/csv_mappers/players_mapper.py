from util import get_players

BLOCK_LENGTH = 0x7C
CHARSET = 'utf-16'


def main():
    with open('../files/ID00051_000', 'rb') as f:
        players = get_players(f)

    with open('../csv/players.csv', 'w+', encoding=CHARSET) as o:
        for _id in players.keys():
            o.write(f'{_id},{players[_id].get("name")},{players[_id].get("block")}\n')


if __name__ == '__main__':
    main()
