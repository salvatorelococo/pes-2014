import os
from string import ascii_uppercase, digits

from classes.Nationality import Nationality
from classes.Team import Team
from config import FILES_DIR, CSV_DIR

FILES_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', FILES_DIR, '')
CSV_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', CSV_DIR, '')

CHARSET = 'utf-8'

# Filter for common bytes only
valid_bytes = [
    *(x.encode(CHARSET) for x in ascii_uppercase),
    *(x.encode(CHARSET) for x in digits),
    b' ',
    b'.',
    b'-',
    b'\''
]

# Special byte for accented letters
special_byte = b'\xc3'


def main():
    # Nationalities
    nationalities = Nationality.get_all()
    with open(CSV_DIRECTORY + 'ID00015_nationalities.csv', 'w+', encoding=CHARSET) as f:
        f.write(
            '\n'.join(
                ','.join(
                    [str(n.id), n.abbr, n.name, n.bytes_sequence]
                ) for n in nationalities
            )
        )

    # Nationals & Clubs
    teams = Team.get_all()
    with open(CSV_DIRECTORY + 'ID00015_teams.csv', 'w+', encoding=CHARSET) as f:
        f.write(
            '\n'.join(
                ','.join(
                    [str(t.id), t.abbr, t.name, t.bytes_sequence]
                ) for t in teams
            )
        )


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e.__str__())
        input('Premi INVIO per terminare')
