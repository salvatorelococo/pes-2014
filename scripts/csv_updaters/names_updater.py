import csv
from os import path

from config import FILES_DIR, CSV_DIR

FILES_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', FILES_DIR, '')
CSV_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', CSV_DIR, '')

CHARSET = 'utf-8'


def main():
    # Import of data from csv
    with open(CSV_DIRECTORY + 'ID00015.csv', encoding=CHARSET) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        data = [*csv_reader]

    # Update of id file
    with open(FILES_DIRECTORY + 'ID00015/', 'rb+') as f:
        print('Modifica in corso...\n')
        for row in data:
            abbr = row[0]
            name = row[1]
            abbr_ptr = int(row[2])
            name_ptr = int(row[3])
            end_ptr = int(row[4])
            
            encoded_name = name.encode(CHARSET)

            f.seek(name_ptr)

            if int(abbr_ptr) != -1:
                name_max_length = abbr_ptr - name_ptr - 1
            else:
                name_max_length = end_ptr - name_ptr - 1

            if len(encoded_name) > name_max_length:
                new_encoded_name = encoded_name[0:name_max_length]
                print(name, 'troncato in', new_encoded_name.decode(CHARSET))
                encoded_name = new_encoded_name

            f.write(encoded_name)
            f.write(b'\x00' * (name_max_length + 1 - len(name)))

            if int(abbr_ptr) != -1:
                f.seek(abbr_ptr)
                f.write(abbr.encode(CHARSET))
                f.write(b'\x00' * (end_ptr - abbr_ptr + len(abbr)))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e.__str__())
        input('Premi INVIO per terminare')
