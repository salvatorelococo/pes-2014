#
# author        : SLC
# description   : Script created for extracting a csv file from PES 2014 team names databases, stored in OVER.cpk.
#
#                 CSV file will have following values (separated by comma):
#                 - Team ID
#                 - Team Name Abbreviation (es: ACM)
#                 - Team Name (es: AC MILAN)
#                 - Team related byte sequence
#                 - Team League (es: 'SERIE A')
#
# date          : 2021-07-16
# version       : 1.2
#

import sys
from string import ascii_uppercase, digits

from names_structure import pointers


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
    i = open(filename, 'rb')

    # Search for nationalities
    print('*' * 32)
    print('Nazionalità'.upper())
    print('*' * 32)

    nationalities_id = 0
    nationalities_length = 8

    k = 'nationalities'
    nationalities = pointers.get(k)
    total_nationalities = (nationalities.get('end') - nationalities.get('start')) / nationalities_length

    with open(filename + '_' + k + '.csv', 'w+', encoding=encoding_type) as f:
        while nationalities_id < total_nationalities:
            i.seek(nationalities.get('start') + nationalities_id * nationalities_length)
            info = i.read(nationalities_length)

            name_position = (info[1] - int('18', 16)) * int('100', 16) + info[0]
            abbr_position = (info[5] - int('18', 16)) * int('100', 16) + info[4]

            i.seek(name_position)
            name = b''
            while True:
                c = i.read(1)

                if c == b'\x00':
                    break

                name += c

            i.seek(abbr_position)
            abbr = b''
            while True:
                c = i.read(1)

                if c == b'\x00':
                    break

                abbr += c

            hex_string = ' '.join(hex(i)[2:].zfill(2).upper() for i in info)

            f.write(f'{nationalities_id},{abbr.decode(encoding_type)},{name.decode(encoding_type)},{hex_string}\n')
            print(f'{nationalities_id:3}. {name.decode(encoding_type)} ({abbr.decode(encoding_type)})')
            print(hex_string)
            print()

            nationalities_id += 1

    print()

    # Search for clubs

    print('*' * 32)
    print('Squadre'.upper())
    print('*' * 32)
    print()

    teams_id = 0
    teams_length = 16

    nationals = pointers.get('nationals')
    clubs = pointers.get('clubs')

    with open(filename + '_teams' + '.csv', 'w+', encoding=encoding_type) as f:
        for teams_dict in [nationals, clubs]:
            for k in (key for key in teams_dict if key not in ['start', 'end']):
                title = teams_dict.get(k).get('title').upper()

                print('*' * 32)
                print(title)
                print('*' * 32)
                print()

                counter = 0

                league = teams_dict.get(k)
                clubs = (league.get('end') - league.get('start')) / teams_length

                while counter < clubs:
                    ptr = league.get('start') + counter * teams_length
                    i.seek(ptr)
                    info = i.read(teams_length)

                    name_position = (info[1] - int('18', 16)) * int('100', 16) + info[0]
                    abbr_position = (info[5] - int('18', 16)) * int('100', 16) + info[4]

                    i.seek(name_position)

                    name = b''
                    while True:
                        c = i.read(1)

                        if c == b'\x00':
                            break

                        name += c

                    i.seek(abbr_position)
                    abbr = b''
                    while True:
                        c = i.read(1)

                        if c == b'\x00':
                            break

                        abbr += c

                    hex_string = ' '.join(hex(i)[2:].zfill(2).upper() for i in info)

                    f.write(f'{teams_id},{abbr.decode(encoding_type)},{name.decode(encoding_type)},{hex_string},{title}\n')
                    print(f'{teams_id:3}. {name.decode(encoding_type)} ({abbr.decode(encoding_type)})')
                    print(hex_string)
                    print()

                    counter += 1
                    teams_id += 1

                print()

    i.close()


if __name__ == '__main__':
    args = sys.argv[1:]

    # Default value
    if len(args) == 0:
        main('ID00015')
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
