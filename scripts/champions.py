import csv

encoding_type = 'utf-8'


def main():
    cl_teams_ids = []
    all_teams = {}

    with open('files/ID00015_teams.csv', encoding=encoding_type) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        data = [*csv_reader]

    for row in data:
        all_teams[row[0]] = row[1:]

    with open('files/EBOOT.OLD', 'rb') as f:
        f.seek(0x2C3358)

        for _ in range(32):
            seq = f.read(8)
            cl_teams_ids.append(hex(seq[4])[2:].upper())

    for _id in cl_teams_ids:
        print(_id, all_teams[_id][1])


if __name__ == '__main__':
    main()
