#
# author        : SLC
# description   : Script created for extracting a csv file from PES 2014 team names databases, stored in OVER.cpk.
#
#                 CSV file will have following values (separated by comma):
#                 - Team Name Abbreviation (es: ACM)
#                 - Team Name (es: AC MILAN)
#                 - Abbreviation pointer (position of the first byte for the abbreviation)
#                 - Team Name pointer (position of the first byte for the team name)
#                 - End pointer (position that should not be overcome)
#
#                 You can use this as source for another script of mine: team_names_updater.py.
# date          : 2021-07-16
# version       : 1.1
#

import sys
from string import ascii_uppercase, digits

# ! ATTENTION !
# Settings - These info should be set according to the file you want to working on
starting_byte = int('1180', 16)
ending_byte = int('3240', 16)

# Encoding settings
encoding_type = 'utf-8'

# Filter for common bytes only
valid_bytes = [
    *(x.encode(encoding_type) for x in ascii_uppercase),
    *(x.encode(encoding_type) for x in digits),
    b' ',
    b'.',
    b'-',
    b'\''
]

# Special byte for accented letters
special_byte = b'\xc3'


def main(filename: str):
    # Opening files
    s = open(filename, 'rb')
    o = open(filename + '.csv', 'w+', encoding=encoding_type)

    # Skipping not relevant data
    s.seek(starting_byte)
    current_pos = starting_byte

    # Starting reading
    try:
        starting_flag = True

        while current_pos < ending_byte:
            team_name = b''
            team_short = b''
            team_name_pos = None
            team_short_pos = None

            while True:
                tmp = s.read(1)

                if tmp == special_byte:
                    team_name += tmp
                    team_name += s.read(1)
                    current_pos += 2

                    # Handling of error while reading the couple of bytes starting with the "special"
                    try:
                        team_name.decode(encoding_type)
                    except:
                        team_name = team_name[:-2]
                        current_pos -= 1
                        s.seek(current_pos)

                    continue

                if tmp not in valid_bytes:
                    current_pos += 1
                    if len(team_name) > 2:
                        break
                    else:
                        continue

                if not team_name_pos:
                    team_name_pos = current_pos

                current_pos += 1

                team_name += tmp

            while True:
                tmp = s.read(1)

                if tmp not in valid_bytes:
                    current_pos += 1
                    if len(team_short) > 1:
                        break
                    else:
                        team_short = b''  # ignore single characters among \x00
                        continue

                # Turnaround for teams without abbreviation
                if len(team_short) > 4:
                    team_short = b''
                    current_pos = team_short_pos
                    s.seek(team_short_pos)
                    team_short_pos = -1  # Arbitrary value for no abbreviation
                    break

                if not team_short_pos:
                    team_short_pos = current_pos

                current_pos += 1
                team_short += tmp

            if current_pos > ending_byte:
                break

            if not starting_flag:
                o.write(str(team_name_pos) + '\n')
                print(str(team_name_pos))
            else:
                starting_flag = False

            print(
                team_short.decode(encoding_type) + ',' +
                team_name.decode(encoding_type) + ',' +
                str(team_short_pos) + ',' +
                str(team_name_pos) + ',', end=''
            )

            o.write(
                team_short.decode(encoding_type) + ',' +
                team_name.decode(encoding_type) + ',' +
                str(team_short_pos) + ',' +
                str(team_name_pos) + ','
            )

        print(ending_byte),
        o.write(str(ending_byte))

    except Exception as e:
        print()
        print('error:', e.__str__())
        print('current position:', hex(current_pos))

    finally:
        # Closing files
        s.close()
        o.close()
        print('\n')
        input('FINE. Premi INVIO per terminare.')


if __name__ == '__main__':
    args = sys.argv[1:]

    # Default value
    if len(args) == 0:
        main('files/ID00015')
    elif len(args) == 1:
        main(args[0])
    else:
        print('\n'.join([
            'Invalid arguments',
            '',
            'Usage:',
            f'\t- {sys.argv[0]} "ID Filename"'
        ]))
        exit(1)
