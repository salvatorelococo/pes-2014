import requests_html
import unicodedata

from util import list_to_bytes, get_nationality_id, get_players_by_name

DEFAULT_BYTES = \
    b'\xB3\x00\x05\x00\x00\x70\x4E\x28\x50\x42\x47\x3E\xC2\x3F\x4B\x41' \
    b'\x44\x3E\x43\x3B\x44\x42\x49\x41\x39\x4C\x40\x43\x4B\x41\x44\x32' \
    b'\x98\x1D\x00\x00\x00\x37\x8E\x10\x20\x50\x70\x77\x01\x00\x00\x00' \
    b'\x3E\x00\x00\x00\x17\x00\x34\x13\x21\x77\x77\x77\x77\x17\x00\x00' \
    b'\x0E\x00\x00\x00\x60\xDB\xB6\x61\x60\xC3\x86\x6D'

CHARSET = 'utf-8'
PLAYERS_BLOCK_LENGTH = 0x7C


def get_player_bytes(player: dict, pl_bytes: [int] = None):
    new_player_flag = False

    if pl_bytes is None:
        new_player_flag = True
        pl_bytes = [0 for _ in range(124)]

    # Nome giocatore (0 - 31)
    counter = 0

    real_name = player.get('Impostazioni di base').get('Vero nome')[:16]
    name = real_name or player.get('Impostazioni di base').get('Nome')[:16]

    for c in name:
        enc_c = c.encode('utf-16')[2:]

        enc_counter = 0
        for enc_byte in enc_c:
            pl_bytes[counter + enc_counter] = enc_byte
            enc_counter += 1

        counter += 2

    # Nome maglietta (32 - 47)
    offset = 32
    counter = 0

    shirt_name = get_shirt_name(name)[:15]
    for c in shirt_name:
        enc_c = c.encode(CHARSET)

        enc_counter = 0
        for enc_byte in enc_c:
            pl_bytes[offset + counter + enc_counter] = enc_byte
            enc_counter += 1

        counter += 1

    # Nome annunciato (48 - 49) | default = ---
    if not new_player_flag:
        pl_bytes[48] = 255
        pl_bytes[49] = 255

    # Stile calcio di rigore (52) | default = 1
    # Stile calcio di punizione (52) | default = 1
    # Piede preferito (52)
    pl_bytes[52] -= pl_bytes[52] % 2
    if player['Impostazioni di base']['Piede preferito'] == 'Sinistra':
        pl_bytes[52] += 1

    # Tipo di rinvio (53) | default = 1
    # Stile dribbling (53) | default = 1
    # Posizione predefinita (53)
    pl_bytes[53] -= (pl_bytes[53] - pl_bytes[53] % (2 ** 4))
    positions_dict = {
        'PT': 0,
        'DC': 3,
        'TS': 4,
        'TD': 4,
        'MED': 5,
        'CC': 7,
        'CLS': 8,
        'CLD': 8,
        'TRQ': 9,
        'ESA': 10,
        'EDA': 10,
        'SP': 11,
        'P': 12
    }
    pl_bytes[53] += positions_dict[player['Posizione']['Principale']] * (2 ** 4)

    # Abilità speciali (66 - 79, 82, 84) | Default: Nessuna
    for i in range(66, 80):
        pl_bytes[i] -= pl_bytes[i] - pl_bytes[i] % (2 ** 7)

    pl_bytes[82] = 0
    pl_bytes[84] -= pl_bytes[84] - pl_bytes[84] % (2 ** 7)

    specials_dict = {
        'Ala prolifica': [(79, 2 ** 7)],
        'Astuzia': [(70, 2 ** 7)],
        'Classico #10': [(72, 2 ** 7)],
        'Collante': [(76, 2 ** 7)],
        'Colpo di tacco': [(82, 2 ** 0)],
        'Colpo di testa': [(82, 2 ** 2)],
        'Cross calibrato': [(79, 2 ** 7)],
        'Disimpegno acrobatico': [(82, 2 ** 5)],
        'Doppio tocco': [(73, 2 ** 7)],
        'Elastico': [(68, 2 ** 7)],
        'Esterno a giro': [(82, 2 ** 1)],
        'Finalizz. acrobatica': [(74, 2 ** 7)],
        'Finta doppio passo': [(68, 2 ** 7)],
        'Finta portoghese': [(68, 2 ** 7)],
        'Fulcro di gioco': [(72, 2 ** 7)],
        'Funambolo': [(68, 2 ** 7)],
        'Giocatore chiave': [(82, 2 ** 2)],
        'Incontrista': [(71, 2 ** 7)],
        'Intercettazione': [(82, 2 ** 5)],
        'Lancio lungo': [(79, 2 ** 7)],
        'Marcatore': [(82, 2 ** 2)],
        'No-look': [(72, 2 ** 7)],
        'Onnipresente': [(70, 2 ** 7)],
        'Opportunista': [(69, 2 ** 7), (74, 2 ** 7)],
        'Pallonetto mirato': [(75, 2 ** 7)],
        'Para-rigori': [(82, 2 ** 6)],
        'Passaggio a scavalcare': [(73, 2 ** 7)],
        'Passaggio calibrato': [(73, 2 ** 7)],
        'Passaggio di prima': [(82, 2 ** 0)],
        'Passaggio filtrante': [(72, 2 ** 7)],
        'Portiere difensivo': [(82, 2 ** 7)],
        'Portiere offensivo': [(82, 2 ** 8)],
        'Rapace dell\'area': [(75, 2 ** 7)],
        'Regista creativo': [(72, 2 ** 7)],
        'Rimbalzo interno': [(75, 2 ** 7)],
        'Rimessa lunga PT': [(84, 2 ** 7)],
        'Rimessa profonda PT': [(84, 2 ** 7)],
        'Senza palla': [(70, 2 ** 7)],
        'Serpentina': [(68, 2 ** 7)],
        'Sombrero': [(68, 2 ** 7)],
        'Specialista dei cross': [(79, 2 ** 7)],
        'Specialista dei rigori': [(66, 2 ** 7)],
        'Spirito combattivo': [(82, 2 ** 3)],
        'Sviluppo': [(77, 2 ** 7)],
        'Taglio al centro': [(67, 2 ** 7)],
        'Taglio alle spalle e giro': [(69, 2 ** 7)],
        'Tiratore': [(78, 2 ** 7)],
        'Tiri a salire': [(78, 2 ** 7)],
        'Tiri a scendere': [(78, 2 ** 7)],
        'Tiro da lontano': [(78, 2 ** 7)],
        'Tiro di prima': [(74, 2 ** 7)],
        'Tiro di collo': [(82, 2 ** 1)],
        'Tornante': [(82, 2 ** 4)],
        'Tra le linee': [(72, 2 ** 7)],
        'Traiettoria bassa': [(84, 2 ** 7)],
        'Uso della suola': [(68, 2 ** 7)],
        'Veronica': [(68, 2 ** 7)],
    }

    ability_not_found_flag = False
    for ab in player['Abilità speciali']:
        try:
            for mod in specials_dict[ab]:
                offset = mod[0]
                bit_value = mod[1]

                pl_bytes[offset] -= pl_bytes[offset] % (bit_value * 2) - pl_bytes[offset] % bit_value
                pl_bytes[offset] += bit_value
        except KeyError:
            print(f'Abilità {ab} non trovata.')
            ability_not_found_flag = True

    if ability_not_found_flag:
        print()

    # Posizioni (54 - 65)
    for i in range(54, 66):
        pl_bytes[i] -= pl_bytes[i] - pl_bytes[i] % (2 ** 7)

    positions_dict = {
        'PT': 54,
        'LIB': 55,
        'DC': 56,
        'TER': 57,
        'TS': 57,
        'TD': 57,
        'MED': 58,
        'EB': 59,
        'CC': 60,
        'CL': 61,
        'CLS': 61,
        'CLD': 61,
        'TRQ': 62,
        'EA': 63,
        'ESA': 63,
        'EDA': 63,
        'SP': 64,
        'P': 65
    }

    for p in player['Posizione']['Tutte']:
        pl_bytes[positions_dict[p]] = 2**7

    # Abilità (54 - 79)
    for i in range(54, 80):
        pl_bytes[i] -= pl_bytes[i] % (2 ** 7)

    abilities_dict = {
        'Accelerazione': [(59, 1), (60, 0.5), (61, 0.33)],
        'Aggressività': [(77, 0.3)],
        'Attacco GEN': [(54, 1)],
        'Calci piazzati': [(71, 1)],
        'Colpo di testa': [(73, 1)],
        'Comportamento offensivo': [(77, 0.7)],
        'Contatto fisico': [(60, 0.5)],
        'Controllo palla': [(62, 1)],
        'Difesa GEN': [(55, 1)],
        'Dribbling GEN': [(76, 0.5)],
        'Elevazione': [(74, 1)],
        'Finalizzazione': [(68, 1), (70, 0.5)],
        'Passaggio alto': [(66, 1), (67, 1)],
        'Passaggio GEN': [(75, 0.5), (76, 0.5)],
        'Passaggio rasoterra': [(64, 1), (65, 1)],
        'Portiere GEN': [(79, 1)],
        'Possesso stretto': [(63, 1)],
        'Potenza di tiro': [(69, 1)],
        'Recupero palla': [(75, 0.5)],
        'Resistenza': [(57, 1)],
        'Saldo': [(56, 1), (61, 0.33)],
        'Tiro a giro': [(70, 0.5), (72, 1)],
        'Velocità': [(58, 1), (61, 0.34)],
    }

    for k in abilities_dict:
        val = player['Abilità'][k]

        for mod in abilities_dict[k]:
            offset = mod[0]
            weight = mod[1]

            pl_bytes[offset] += val * weight

    # Mentalità (78)
    mentality_dict = {
        'Comportamento difensivo': [0.3, 0.8, 0.4, 0.1],
        'Comportamento offensivo': [0.1, 0.1, 0.4, 0.8],
        'Comportamento PT': [0.6, 0, 0, 0],
        'Saldo': [0.1, 0.1, 0.2, 0.1]
    }

    positions_dict = {
        0: ['PT'],
        1: ['TS', 'DC', 'TD'],
        2: ['CLS', 'MED', 'CC', 'TRQ', 'CLD'],
        3: ['ESA', 'SP', 'P', 'EDA']
    }

    pl_bytes[78] -= pl_bytes[78] % (2 ** 7)
    for k in positions_dict:
        if player['Posizione']['Principale'] in positions_dict[k]:
            for ability in mentality_dict:
                val = player['Abilità'][ability]
                pl_bytes[78] += val * mentality_dict[ability][k]

    # Abilità (80-81)
    abilities_dict_2 = {
        'Frequenza piede debole': [(80, 2, 2 ** 6, 2 ** 3)],
        'Precisione piede debole': [(81, 2, 2 ** 6, 2 ** 3)],
        'Forma fisica': [(81, 1, 2 ** 3, 2 ** 0)]
    }

    for k in abilities_dict_2:
        val = player['Abilità'][k]

        for mod in abilities_dict_2[k]:
            offset = mod[0]
            multiplier = mod[1]
            max_bit_weight = mod[2]
            weight = mod[3]

            pl_bytes[offset] -= (pl_bytes[offset] % max_bit_weight) - (pl_bytes[offset] % weight)
            pl_bytes[offset] += (val * multiplier - 1) * weight

    # Resistenza infortuni (80)
    pl_bytes[80] -= pl_bytes[80] - pl_bytes[80] % (2 ** 6)
    pl_bytes[80] += (player['Abilità']['Resistenza infortuni'] - 1) * (2 ** 6)

    # Fascia preferita (81) | Default: Fascia piede preferito

    # Esultanza 1 (83) | Default: 0
    # Esultanza 2 (84) | Default: 0

    # Miglioramento giocatore (85) | Default: Lento / Costante

    # Altezza (88)
    pl_bytes[88] -= pl_bytes[88] % (2 ** 7)
    pl_bytes[88] += player['Aspetto']['Fisico']['Altezza'] - 148

    # Peso (89)
    pl_bytes[89] -= pl_bytes[89] % (2 ** 7)
    pl_bytes[89] += player['Aspetto']['Fisico']['Peso']

    # Nazionalità (112)
    pl_bytes[112] = get_nationality_id(player['Impostazioni di base']['Nazionalità'])

    # Età (113)
    age = player['Impostazioni di base']['Età']
    pl_bytes[113] -= pl_bytes[113] % (2 ** 6) - pl_bytes[113] % 2
    pl_bytes[113] += (age - 15) * 2

    # Impostazioni aspetto fisico | Default
    if new_player_flag:
        pl_bytes[90] = 0x70
        pl_bytes[91] = 0x77
        pl_bytes[92] = 0xD4
        pl_bytes[93] = 0x06
        pl_bytes[99] = 0x40
        pl_bytes[100] = 0x10
        pl_bytes[105] = 0x77
        pl_bytes[106] = 0x77
        pl_bytes[107] = 0x77
        pl_bytes[108] = 0x77
        pl_bytes[109] = 0x07
        pl_bytes[116] = 0x60
        pl_bytes[117] = 0xDB
        pl_bytes[118] = 0xB6
        pl_bytes[119] = 0x61
        pl_bytes[120] = 0x60
        pl_bytes[121] = 0xC3
        pl_bytes[122] = 0x86
        pl_bytes[123] = 0x6D

    pl_bytes = [int(x) for x in pl_bytes]
    return list_to_bytes(pl_bytes)


def get_player(player_page):
    positions = player_page.html.find('.player-positions-new', first=True)
    player_info = player_page.html.find('table.player-info > tbody > tr')

    player_skills = player_page.html.find('.stats-block table.player-stats-modern > tbody > tr')
    player_special_skills = player_page.html.find('.player-index-list > li')

    real_name = [x.find('td')[1].text for x in player_info if x.find('td', first=True).text == 'Vero Nome']
    real_name = real_name[0] if real_name else ''

    print('RIEPILOGO GIOCATORE')
    player = {
        'Impostazioni di base': {
            'Nome': player_page.html.find('.top-header > span:not(:first-child)', first=True).text,
            'Vero nome': real_name,
            'Età': int([x.find('td')[1].text for x in player_info if x.find('td', first=True).text == 'Età'][0]),
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
            x.find('td')[1].text: int(x.find('td > span', first=True).text) for x in player_skills
        },
        'Abilità speciali': [x.text for x in player_special_skills],
        'Aspetto': {
            'Fisico': {
                'Altezza': int([x.find('td')[1].text for x in player_info if
                                x.find('td', first=True).text == 'Altezza (cm)'][0]),
                'Peso': int([x.find('td')[1].text for x in player_info if
                             x.find('td', first=True).text == 'Peso'][0])
            }
        }
    }

    skills_blocks = player_page.html.find('.stats-block')

    ovr_atk = int(skills_blocks[0].find('h4 > span', first=True).text)
    ovr_drb = int(skills_blocks[1].find('h4 > span', first=True).text)
    ovr_def = int(skills_blocks[2].find('h4 > span', first=True).text)
    ovr_pas = int(skills_blocks[3].find('h4 > span', first=True).text)
    ovr_phy = int(skills_blocks[4].find('h4 > span', first=True).text)
    ovr_gk = int(skills_blocks[5].find('h4 > span', first=True).text)

    player['Abilità']['Attacco GEN'] = ovr_atk
    player['Abilità']['Dribbling GEN'] = ovr_drb
    player['Abilità']['Difesa GEN'] = ovr_def
    player['Abilità']['Passaggio GEN'] = ovr_pas
    player['Abilità']['Fisico GEN'] = ovr_phy
    player['Abilità']['Portiere GEN'] = ovr_gk if ovr_gk != 40 else 50

    print_player_stats(player)
    return player


def print_player_stats(player: dict):
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


def get_shirt_name(s: str):
    s = "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = s.upper()

    if s[1:3] == '. ':
        s = s[3:]

    return s


def main():

    session = requests_html.HTMLSession()
    pes_master_url = 'https://www.pesmaster.com/it/pes-2021/'

    player_bytes = b''
    new_player_flag = True
    offset = 0

    while True:
        name = input('Digita il nome del giocatore per inserire un nuovo giocatore o EXIT per uscire: ')
        print()

        if name.lower() == 'exit':
            break

        search_page = session.get(pes_master_url, params={'q': name})
        player_container = search_page.html.find('.player-card-container', first=True)
        player_flag = False

        if not player_container:
            while True:
                x = input('Giocatore non trovato! Aggiungere comunque con impostazioni default? (s/n): ').lower()

                if x in ['s', 'n']:
                    print()
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
                try:
                    x = int(
                        input('Inserisci il valore corrispondente al giocatore che vuoi aggiungere (-1 per annullare): '))

                    if -1 <= x < len(figures):
                        print()
                        break

                except ValueError:
                    pass

            if x == -1:
                continue

            sel_player = players[x]

            player_page = session.get(sel_player["url"])
            player = get_player(player_page)
            player_flag = True

            name = player['Impostazioni di base']['Nome']
            existing_players = get_players_by_name(name)

            if len(existing_players) > 0:
                print(f'Sono stati trovati {len(existing_players)} giocatori con nome simile: ')

                for i in range(len(existing_players)):
                    print(f'{str(i):3} | {str(existing_players[i]["id"]):5} | {existing_players[i]["name"]:30}')

                print()

                while True:
                    try:
                        x = int(
                            input(
                                'Inserisci il valore corrispondente al giocatore da aggiornare (-1 per aggiungerlo, '
                                '-2 per annullare): '))

                        if -2 <= x < len(existing_players):
                            break
                    except ValueError:
                        pass

                print()

                if x == -2:
                    continue
                elif x == -1:
                    player_bytes = get_player_bytes(player)
                else:
                    new_player_flag = False
                    offset = PLAYERS_BLOCK_LENGTH * int(existing_players[x]["id"])

                    block = [*existing_players[x]["block"]]
                    player_bytes = get_player_bytes(player, block)
            else:
                player_bytes = get_player_bytes(player)
                print('Nessun giocatore già presente con nome simile trovato. Il giocatore verrà aggiunto.\n')

            while True:
                x = input('Confermi l\'inserimento? (s/n): ').lower()

                if x in ['s', 'n']:
                    print()
                    break

        if x == 'n':
            continue

        if not player_flag:
            shirt = name.upper()

            enc_name = b''.join(n.encode(CHARSET) + b'\x00' for n in name)
            enc_name = enc_name + b'\x00' * (32 - len(enc_name))

            enc_shirt = shirt.encode(CHARSET)[:15]
            enc_shirt = enc_shirt + b'\x00' * (16 - len(enc_shirt))
            player_bytes = enc_name + enc_shirt + DEFAULT_BYTES

        try:
            if new_player_flag:
                with open('files/ID00051_000', 'ab') as f:
                    f.write(player_bytes)

                print(name + ' aggiunto!\n')
            else:
                with open('files/ID00051_000', 'rb+') as f:
                    f.seek(offset)
                    f.write(player_bytes)

                print(name + ' aggiornato!\n')
        except Exception as e:
            print(e.__str__())


if __name__ == '__main__':
    main()
