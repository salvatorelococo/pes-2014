#
# author        : SLC
# description   : Script created for editing PES 2014 team names databases, stored in OVER.cpk, by using a csv file.
#
#                 CSV file must have following values (separated by comma) in this order:
#                 - Team Name Abbreviation (es: ACM)
#                 - Team Name (es: AC MILAN)
#                 - Abbreviation pointer (position of the first byte for the abbreviation)
#                 - Team Name pointer (position of the first byte for the team name)
#                 - End pointer (position that should not be overcome)
#
#                 You can get a source csv by using another script of mine: team_names_scraper.py (v.1.1).
# date          : 2021-07-16
# version       : 1.2
#

import csv
import re
import sys

from names_structure import pointers

encoding_type = 'utf-8'


def main(csv_x: str, db_x: str):
    # Import of data from csv
    with open(csv_x, encoding=encoding_type) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        data = [*csv_reader]

    nationalities_ptr = 0
    clubs_ptr = 0

    with open(db_x, 'wb+') as f:
        nationalities = pointers.get('nationalities')
        clubs = pointers.get('clubs')

        for row in data:
            if row[2] == 'nationalities':
                print('nat')
            elif row[2] == 'clubs':
                print('club')

    # Update of id file
    with open(db_x, 'rb+') as f:
        print('Modifica in corso...\n')

        tmp_name = b''
        tmp_pointers = b''

        for row in data:
            abbr = row[0]
            name = row[1]

            len(tmp_name)





def throw_usage_error():
    print('\n'.join([
        'Invalid arguments',
        '',
        'Use:',
        '\t- A .txt file containing the name of the csv file followed by the name of the id file',
        '\t- The name of the csv file followed by the name of the id file',
        '',
        'Examples:',
        f'\t- {sys.argv[0]} "text file.txt"',
        f'\t- {sys.argv[0]} "ID00015.csv" "ID00015"'
    ]))

    exit(1)


if __name__ == '__main__':
    args = sys.argv[1:]

    # Default values (ID00015 match the spanish database)
    if len(args) == 0:
        main('ID00015.csv', 'ID00015')

    # Import filenames from txt
    elif len(args) == 1:
        with open(args[0]) as txt:
            txt_content = txt.read().strip()
            space_split_content = txt_content.split(' ')

            if len(space_split_content) < 2:
                throw_usage_error()
                
            csv_x = {'filename': [], 'done': False}
            db_x = {'filename': [], 'done': False}
            double_quotes_flag = False

            for sub_content in space_split_content:
                if csv_x['done'] and db_x['done']:
                    throw_usage_error()
                
                quotes = re.findall('"', sub_content)

                if len(quotes) == 0:
                    if not csv_x['done']:
                        csv_x['filename'] += [sub_content]
                        
                        if not double_quotes_flag:
                            csv_x['done'] = True
                    else:
                        db_x['filename'] += [sub_content]
                        
                        if not double_quotes_flag:
                            db_x['done'] = True
                        
                elif len(quotes) == 1:
                    # Invalid position of double quotes (not opening/closing)
                    c1 = sub_content[0] != '"' and not double_quotes_flag
                    c2 = sub_content[-1] != '"' and double_quotes_flag
                    
                    if c1 or c2:
                        throw_usage_error()

                    is_closing = sub_content[-1] == '"' and double_quotes_flag
                    double_quotes_flag = not double_quotes_flag
                    clean_sub_content = sub_content.replace('"', '')
                    
                    if not csv_x['done']:
                        csv_x['filename'] += [clean_sub_content]
                        
                        if is_closing:
                            csv_x['done'] = True
                    else:
                        db_x['filename'] += [clean_sub_content]
                        
                        if is_closing:
                            db_x['done'] = True
                
                elif len(quotes) == 2:
                    # Invalid position of double quotes
                    if not (sub_content[0] == '"' and sub_content[-1] == '"') or double_quotes_flag:
                        throw_usage_error()

                    if not csv_x['done']:
                        csv_x['filename'] = sub_content.replace('"', '')
                        csv_x['done'] = True
                    else:
                        db_x['filename'] = sub_content.replace('"', '')
                        db_x['done'] = True

                elif len(quotes) > 2:
                    throw_usage_error()
            
            main(' '.join(csv_x['filename']), ' '.join(db_x['filename']))

    # Use filenames as arguments
    elif len(args) == 2:
        main(*args)

    # Invalid number of arguments
    else:
        throw_usage_error()

    input('\nFINE. Premi INVIO per terminare.')
