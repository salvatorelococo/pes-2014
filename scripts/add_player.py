import requests_html

DEFAULT_BYTES = \
    b'\xB3\x00\x05\x00\x00\x70\x4E\x28\x50\x42\x47\x3E\xC2\x3F\x4B\x41' \
    b'\x44\x3E\x43\x3B\x44\x42\x49\x41\x39\x4C\x40\x43\x4B\x41\x44\x32' \
    b'\x98\x1D\x00\x00\x00\x37\x8E\x10\x20\x50\x70\x77\x01\x00\x00\x00' \
    b'\x3E\x00\x00\x00\x17\x00\x34\x13\x21\x77\x77\x77\x77\x17\x00\x00' \
    b'\x0E\x00\x00\x00\x60\xDB\xB6\x61\x60\xC3\x86\x6D'

CHARSET = 'utf-8'


def main():
    session = requests_html.HTMLSession()
    pes_master_url = 'https://www.pesmaster.com/it/pes-2021/'

    while True:
        name = input('Digita il nome del giocatore per inserire un nuovo giocatore o EXIT per uscire: ')
        print()

        if name.lower() == 'exit':
            break

        search_page = session.get(pes_master_url, params={'q': name})
        player_container = search_page.html.find('.player-card-container', first=True)

        if not player_container:
            while True:
                x = input('Giocatore non trovato! Aggiungere comunque con impostazioni default? (s/n): ').lower()

                if x in ['s', 'n']:
                    break

        else:
            figures = player_container.find('.player-card')
            players = {}
            counter = 0

            print(f'Sono stati trovati {len(figures)} risultati:')
            for f in figures:
                player = {
                    'name': f.find('.player-card-name', first=True).text,
                    'ovr': f.find('.player-card-ovr', first=True).text,
                    'pos': f.find('.player-card-position', first=True).text,
                    'url': [*f.absolute_links][0]
                }

                players[counter] = player
                print(
                    f'{str(counter):3} | {player["name"]:20} | {player["ovr"]:2} | {player["pos"]:3} | {player["url"]}')
                counter += 1

            print()

            while True:
                x = int(
                    input('Inserisci il valore corrispondente al giocatore che vuoi aggiungere (-1 per annullare): '))

                if -1 <= x < len(figures):
                    break

            if x == -1:
                continue

            print()
            sel_player = players[x]

            player_page = session.get(sel_player["url"])
            positions = player_page.html.find('.player-positions-new', first=True)
            player_info = player_page.html.find('table.player-info > tbody > tr')
            player_skills = player_page.html.find('.stats-block:not(:last-child) table.player-stats-modern > tbody > tr')
            gk_skill = player_page.html.find('.stats-block:last-child > h4 > span', first=True).text
            player_special_skills = player_page.html.find('.player-index-list > li')

            print('RIEPILOGO GIOCATORE')
            player = {
                'Impostazioni di base': {
                    'Nome': player_page.html.find('.top-header > span:not(:first-child)', first=True).text,
                    'Età': [x.find('td')[1].text for x in player_info if x.find('td', first=True).text == 'Età'][0],
                    'Piede preferito': [x.find('td')[1].text for x in player_info if
                                        x.find('td', first=True).text == 'Piede preferito'][0],
                    'Nazionalità': [x.find('td')[1].text for x in player_info if
                                    x.find('td', first=True).text == 'Nazionalità'][0],
                    'Squadra': [x.find('td')[1].text for x in player_info if
                                x.find('td', first=True).text == 'Squadra'][0],
                },
                'Posizione': {
                    'Principale': positions.find('.main > span', first=True).text,
                    'Tutte': [x.find('span', first=True).text for x in
                              positions.find('.fw-1, .fw-2, .mf-2, .mf-1, .df-2, '
                                             '.df-1, .gk-2, .gk-1')]
                },
                'Abilità': {
                    x.find('td')[1].text: x.find('td > span', first=True).text for x in player_skills
                },
                'Abilità speciali': [x.text for x in player_special_skills],
                'Aspetto': {
                    'Fisico': {
                        'Altezza': [x.find('td')[1].text for x in player_info if
                                    x.find('td', first=True).text == 'Altezza (cm)'][0],
                        'Peso': [x.find('td')[1].text for x in player_info if
                                 x.find('td', first=True).text == 'Peso'][0],
                    }
                },
            }

            player['Abilità']['Abilità portiere'] = gk_skill if gk_skill != '40' else '50'

            # TODO: Should make it recursive?
            for key_1 in player:
                if type(player[key_1]) == dict:
                    print(f'*** {key_1.upper()} ***')

                    for key_2 in player[key_1]:
                        if type(player[key_1][key_2]) == dict:
                            print(f'* {key_2} *')

                            for key_3 in player[key_1][key_2]:
                                print(f'{key_3:30}: {player[key_1][key_2][key_3]}')
                        elif type(player[key_1][key_2]) == list:
                            print(f'{key_2:30}: {", ".join(player[key_1][key_2])}')
                        else:
                            print(f'{key_2:30}: {player[key_1][key_2]}')

                    print()
                elif type(player[key_1]) == list:
                    print(f'{key_1:30}: {", ".join(player[key_1])}\n')
                else:
                    print(f'{key_1:30}: {player[key_1]}\n')

            while True:
                x = input('Confermi l\'inserimento? (s/n)').lower()

                if x in ['s', 'n']:
                    break

        if x == 'n':
            continue

        # Values are not used yet!
        # TODO: Continue from here
        shirt = name.upper()

        enc_name = b''.join(n.encode(CHARSET) + b'\x00' for n in name)
        enc_name = enc_name + b'\x00' * (32 - len(enc_name))

        enc_shirt = shirt.encode(CHARSET)[:15]
        enc_shirt = enc_shirt + b'\x00' * (16 - len(enc_shirt))

        try:
            with open('ID00051_000', 'ab') as f:
                f.write(enc_name)
                f.write(enc_shirt)
                f.write(DEFAULT_BYTES)

            print(name + ' aggiunto!\n')
        except Exception as e:
            print(e.__str__())


if __name__ == '__main__':
    main()
