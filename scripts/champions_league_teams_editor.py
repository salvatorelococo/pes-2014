from os import path

from config import FILES_DIR, CSV_DIR
from files_structure.EBOOT_OLD_structure import pointers as eboot_old_pointers
from files_structure.ID00015_structure import pointers as id00015_pointers
from util import get_cl_clubs, get_clubs, get_clubs_by_name, list_to_bytes, hex_string_to_list

FILES_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), FILES_DIR, '')
CSV_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), CSV_DIR, '')


def main():
    with open(FILES_DIRECTORY + 'ID00015', 'rb+') as ID00015, open(FILES_DIRECTORY + 'EBOOT.OLD', 'rb+') as EBOOT_OLD:
        cl_clubs = get_cl_clubs(EBOOT_OLD)
        clubs = get_clubs(ID00015)

        while True:
            print('Squadre attuali: ')
            counter = 0
            cl_clubs_arr = []

            for cl_club in cl_clubs:
                _id = cl_club['id']
                tmp = clubs[_id]
                tmp['id'] = _id
                cl_clubs_arr.append(tmp)

                print(f'{counter:3} | {str(_id):3} {clubs[_id]["name"]}')
                counter += 1

            print()
            while True:
                try:
                    z = int(input('Digita il primo numero sulla riga della squadra che vuoi sostituire (-1 per '
                                  'uscire): '))

                    if -1 <= z < len(cl_clubs_arr):
                        break
                except ValueError:
                    continue

            if z == -1:
                exit()

            print(f'Sostituirai {cl_clubs_arr[z]["name"]}')

            print()
            while True:
                x = input('Inserisci il nome della squadra da inserire (-1 per annullare): ').upper()

                if x == '-1':
                    break

                res = get_clubs_by_name(x, ID00015)

                # Takes only European clubs
                res = [r for r in res if 66 < r["id"] < 197]

                if len(res) > 0:
                    counter = 0
                    for k in res:
                        print(f'{counter:3} | {k["id"]:3} {k["name"]}')
                        counter += 1

                    print()
                    while True:
                        try:
                            y = int(input('Digita il numero che precede la squadra che vuoi inserire (-1 per '
                                          'annullare): '))

                            if -1 <= y < len(res):
                                break
                        except ValueError:
                            continue

                    if y == -1:
                        print()
                        continue

                    selected_club = res[y]
                    break
                else:
                    print(f'Nessuna squadra trovata per {x}...')

            print()
            while True:
                inp = input(f'Sostituirai {cl_clubs_arr[z]["name"]} con {selected_club["name"]}. Confermi? (s/n): ').lower()

                if inp in ['s', 'n']:
                    print()
                    break

            if inp == 'n':
                continue

            break

        # CL Substitution
        block_length_club = 16
        block_length_ucl = 8

        new_id = selected_club["id"]
        new_bytes = selected_club["hex_seq"]

        id00015_position = id00015_pointers['clubs']['champions_league']['start'] + (block_length_club * z)
        ID00015.seek(id00015_position)
        ID00015.write(list_to_bytes(hex_string_to_list(new_bytes)))

        eboot_old_position = eboot_old_pointers['Champions League']['start'] + (block_length_ucl * z) + 4
        EBOOT_OLD.seek(eboot_old_position)
        EBOOT_OLD.write(list_to_bytes([new_id]))

        print('Sostituzione effettuata!')
        input('Premi INVIO per continuare.\n')


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            print(e.__str__())
            input('Premi INVIO per terminare')

