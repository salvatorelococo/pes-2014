from os import path

from classes.Player import Player
from classes.Team import Club, National
from config import CSV_DIR, FILES_DIR

FILES_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), FILES_DIR, '')
CSV_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), CSV_DIR, '')


def get_id_as_bytes(v: int):
    hex_value = hex(v)[2:]

    if len(hex_value) % 2:
        hex_value = '0' + hex_value

    hex_list = [chr(int(hex_value[2 * i:2 * i + 2], 16)).encode('utf-16-le')[::2] for i in range(len(hex_value) // 2)]
    hex_list.reverse()

    if len(hex_list) == 1:
        hex_list.append(b'\x00')

    return b''.join(hex_list)


def main():
    nationals = National.get_all()
    clubs = Club.get_all()

    current_id_value = 1

    with open(FILES_DIRECTORY + 'ID00051_000', 'ab+') as f:
        f.write(Player().get_block())

    IDs = {}

    for team in nationals + clubs:
        players = team.get_players()

        counter = 0
        for player in players:
            if player is None:
                continue

            new_id = IDs.get(player.id)

            if not new_id:
                with open('ID00051_000', 'ab+') as f:
                    f.write(player.get_block())

                new_id = current_id_value
                IDs[player.id] = new_id
                current_id_value += 1

            print(player.id, player, new_id)

            if type(team) == National:
                with open('ID00051_001', 'ab+') as f:
                    f.write(get_id_as_bytes(new_id))

            elif type(team) == Club:
                with open('ID00051_002', 'ab+') as f:
                    f.write(get_id_as_bytes(new_id))

            counter += 1

        print(team, counter, '\n')

        if type(team) == National and counter < 23:
            with open('ID00051_001', 'ab+') as f:
                f.write(b'\x00\x00' * (23 - counter))

        if type(team) == Club and counter < 32:
            with open('ID00051_002', 'ab+') as f:
                f.write(b'\x00\x00' * (32 - counter))

    with open('ID00051_000', 'ab+') as f:
        for player in Player.get_all():
            if player.id not in IDs:
                # print(player.id, player)
                f.write(player.get_block())
                IDs[player.id] = current_id_value
                current_id_value += 1


if __name__ == '__main__':
    main()
