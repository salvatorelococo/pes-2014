from os import path

import requests_html

from classes.Nationality import Nationality, FREE_NATION
from classes.Player import Player, PlayerFoot, PlayerSide, PlayerFavouritePosition
from config import FILES_DIR

FILES_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', FILES_DIR, '')

CHARSET = 'utf-8'

PES_MASTER_URL = 'https://www.pesmaster.com/it/pes-2021/'


def get_nationality_id(nationality: str) -> int:
    nationalities = Nationality.from_name(nationality)

    if len(nationalities) == 0:
        return FREE_NATION

    if len(nationalities) == 1:
        return nationalities[0].id

    print(f'Sono state trovate {len(nationalities)} nazionalità:')
    print(f'\n'.join(f'{i:3} | {nationalities[i].name}' for i in range(len(nationalities))))
    print()

    while True:
        try:
            x = int(input(
                'Digita il numero corrispondente alla nazionalità che vuoi selezionare (-1 per nessuna nazionalità): '))

            if -1 <= x < len(nationalities):
                break
        except ValueError:
            pass

    return FREE_NATION if x == -1 else nationalities[x].id


def get_player_name(player_page) -> str:
    info_container = player_page.html.find('table.player-info > tbody > tr')
    real_name = [x.find('td')[1].text for x in info_container if x.find('td', first=True).text == 'Vero Nome']
    name = player_page.html.find('.top-header > span:not(:first-child)', first=True).text

    return real_name[0] if real_name else name


def get_player(player_page, player: Player = Player()) -> Player:
    info_container = player_page.html.find('table.player-info > tbody > tr')
    positions_container = player_page.html.find('.player-positions-new', first=True)
    skills_blocks = player_page.html.find('.stats-block')
    skills_container = player_page.html.find('.stats-block table.player-stats-modern > tbody > tr')
    special_skills_container = player_page.html.find('.player-index-list > li')

    # Name Settings
    player.name = get_player_name(player_page)
    player.shirt_name = Player.generate_shirt_name(player.name)
    player.basic_settings.age = int(
        [x.find('td')[1].text for x in info_container if x.find('td', first=True).text == 'Età'][0]
    )

    # Basic Settings
    fav_foot = [x.find('td')[1].text for x in info_container if x.find('td', first=True).text == 'Piede preferito'][0]
    player.basic_settings.favourite_foot = PlayerFoot.RIGHT if fav_foot == 'Destra' else PlayerFoot.LEFT

    player.basic_settings.injury_resistance = [
                                                  int(x.find('td > span', first=True).text) for x in skills_container
                                                  if x.find('td:not(.stat)', first=True).text == 'Resistenza infortuni'
                                              ][0] - 1

    # Position Settings
    player_pos = {
        'PT': PlayerFavouritePosition.POR,
        'DC': PlayerFavouritePosition.DC,
        'TS': PlayerFavouritePosition.TER,
        'TD': PlayerFavouritePosition.TER,
        'MED': PlayerFavouritePosition.MED,
        'CC': PlayerFavouritePosition.CC,
        'CLS': PlayerFavouritePosition.CL,
        'CLD': PlayerFavouritePosition.CL,
        'TRQ': PlayerFavouritePosition.TRQ,
        'ESA': PlayerFavouritePosition.EA,
        'EDA': PlayerFavouritePosition.EA,
        'SP': PlayerFavouritePosition.SP,
        'P': PlayerFavouritePosition.P
    }

    player.position.favourite = player_pos.get(positions_container.find('.main > span', first=True).text)

    positions = [
        x.find('span', first=True).text for x in
        positions_container.find('.fw-1, .fw-2, .mf-2, .mf-1, .df-2, .df-1, .gk-2, .gk-1')
    ]
    player.position.all = {
        'POR': 1 if 'PT' in positions else 0,
        'LIB': 1 if 'LIB' in positions else 0,
        'DC': 1 if 'DC' in positions else 0,
        'TER': 1 if any(x in positions for x in ['TER', 'TS', 'TD']) else 0,
        'MED': 1 if 'MED' in positions else 0,
        'EB': 1 if 'EB' in positions else 0,
        'CC': 1 if 'CC' in positions else 0,
        'CL': 1 if any(x in positions for x in ['CL', 'CLS', 'CLD']) else 0,
        'TRQ': 1 if 'TRQ' in positions else 0,
        'EA': 1 if any(x in positions for x in ['EA', 'ESA', 'EDA']) else 0,
        'SP': 1 if 'SP' in positions else 0,
        'P': 1 if 'P' in positions else 0
    }

    both_c0 = not any(x in positions for x in ['TS', 'TD', 'CLS', 'CLD', 'ESA', 'EDA'])
    both_c1 = all(x in positions for x in ['TS', 'TD'])
    both_c2 = all(x in positions for x in ['CLS', 'CLD'])
    both_c3 = all(x in positions for x in ['ESA', 'EDA'])

    if both_c0 or both_c1 or both_c2 or both_c3:
        player.position.side = PlayerSide.BOTH
    else:
        fav_l = player.basic_settings.favourite_foot == PlayerFoot.LEFT
        pos_r = player.position.favourite in ['TD', 'CLD', 'EDA']
        pos_l = player.position.favourite in ['TS', 'CLS', 'ESA']

        if (fav_l and pos_l) or not (fav_l and pos_r):
            player.position.side = PlayerSide.FAVOURITE_FOOT
        else:
            player.position.side = PlayerSide.OPPOSITE_FOOT

    # Nationality
    nationality = [x.find('td')[1].text for x in info_container if x.find('td', first=True).text == 'Nazionalità'][0]
    player.nationality = get_nationality_id(nationality)

    # Appearance
    player.appearance.physique.height = int(
        [x.find('td')[1].text for x in info_container if x.find('td', first=True).text == 'Altezza (cm)'][0]
    )

    player.appearance.physique.weight = int(
        [x.find('td')[1].text for x in info_container if x.find('td', first=True).text == 'Peso'][0]
    )

    # Skills
    skills = {x.find('td')[1].text: int(x.find('td > span', first=True).text) for x in skills_container}
    skills['Attacco GEN'] = int(skills_blocks[0].find('h4 > span', first=True).text)
    skills['Dribbling GEN'] = int(skills_blocks[1].find('h4 > span', first=True).text)
    skills['Difesa GEN'] = int(skills_blocks[2].find('h4 > span', first=True).text)
    skills['Passaggio GEN'] = int(skills_blocks[3].find('h4 > span', first=True).text)
    skills['Fisico GEN'] = int(skills_blocks[4].find('h4 > span', first=True).text)

    ovr_gk = int(skills_blocks[5].find('h4 > span', first=True).text)
    skills['Portiere GEN'] = ovr_gk if ovr_gk != 40 else 50

    player.skills.offense = skills['Attacco GEN']
    player.skills.defense = skills['Difesa GEN']
    player.skills.body_balance = skills['Saldo']
    player.skills.stamina = skills['Resistenza']
    player.skills.top_speed = skills['Velocità']
    player.skills.acceleration = skills['Accelerazione']
    player.skills.responsiveness = int(
        0.5 * skills['Accelerazione'] +
        0.5 * skills['Contatto fisico']
    )
    player.skills.agility = int(
        0.33 * skills['Accelerazione'] +
        0.33 * skills['Saldo'] +
        0.34 * skills['Velocità']
    )
    player.skills.dribble_prec = skills['Controllo palla']
    player.skills.dribble_speed = skills['Possesso stretto']
    player.skills.short_pass_acc = skills['Passaggio rasoterra']
    player.skills.short_pass_speed = skills['Passaggio rasoterra']
    player.skills.long_pass_acc = skills['Passaggio alto']
    player.skills.long_pass_speed = skills['Passaggio alto']
    player.skills.shot_acc = skills['Finalizzazione']
    player.skills.shot_power = skills['Potenza di tiro']
    player.skills.shot_technique = int(
        0.5 * skills['Tiro a giro'] +
        0.5 * skills['Finalizzazione']
    )
    player.skills.free_kick_acc = skills['Calci piazzati']
    player.skills.swerve = skills['Tiro a giro']
    player.skills.header = skills['Colpo di testa']
    player.skills.jump = skills['Elevazione']
    player.skills.teamwork = int(
        0.5 * skills['Passaggio GEN'] +
        0.5 * skills['Recupero palla']
    )
    player.skills.technique = int(
        0.5 * skills['Passaggio GEN'] +
        0.5 * skills['Dribbling GEN']
    )
    player.skills.aggression = int(
        0.3 * skills['Aggressività'] +
        0.7 * skills['Comportamento offensivo']
    )

    mentality_dict = {
        PlayerFavouritePosition.POR: [0.2, 0.0, 0.8, 0.0],
        PlayerFavouritePosition.DC: [0.8, 0.1, 0.0, 0.1],
        PlayerFavouritePosition.TER: [0.6, 0.3, 0.0, 0.1],
        PlayerFavouritePosition.MED: [0.6, 0.2, 0.0, 0.2],
        PlayerFavouritePosition.CC: [0.4, 0.4, 0.0, 0.2],
        PlayerFavouritePosition.CL: [0.3, 0.6, 0.0, 0.1],
        PlayerFavouritePosition.TRQ: [0.2, 0.7, 0.0, 0.1],
        PlayerFavouritePosition.EA: [0.1, 0.8, 0.0, 0.1],
        PlayerFavouritePosition.SP: [0.1, 0.8, 0.0, 0.1],
        PlayerFavouritePosition.P: [0.1, 0.9, 0.0, 0.0]
    }

    mentality_array = mentality_dict[PlayerFavouritePosition[player.position.favourite]]

    player.skills.mentality = int(
        mentality_array[0] * skills['Comportamento difensivo'] +
        mentality_array[1] * skills['Comportamento offensivo'] +
        mentality_array[2] * skills['Comportamento PT'] +
        mentality_array[3] * skills['Saldo']
    )

    player.skills.goalkeeping = skills['Portiere GEN']
    player.skills.weak_foot_frequency = skills['Frequenza piede debole']
    player.skills.weak_foot_accuracy = skills['Precisione piede debole']
    player.skills.condition = skills['Forma fisica']

    # Special Skills
    special_skills = [x.text for x in special_skills_container if x.text != '-']
    player.special_skills.penalties = 'Specialista dei rigori' in special_skills
    player.special_skills.center = 'Talio al centro' in special_skills
    player.special_skills.dribbling = any(x in special_skills for x in [
        'Elastico',
        'Finta doppio passo',
        'Finta portoghese',
        'Funambolo',
        'Serpentina',
        'Sombrero'
    ])
    player.special_skills.possession = any(x in special_skills for x in [
        'Opportunista',
        'Taglio alle spalle e giro'
    ])
    player.special_skills.positioning = any(x in special_skills for x in [
        'Astuzia',
        'Onnipresente',
        'Senza palla'
    ])
    player.special_skills.reaction = 'Incontrista' in special_skills
    player.special_skills.playmaker = any(x in special_skills for x in [
        'Classico #10',
        'Fulcro di gioco',
        'Giocatore chiave'
        'No-look',
        'Passaggio filtrante',
        'Regista creativo',
        'Tra le linee'
    ])
    player.special_skills.passing = any(x in special_skills for x in [
        'Doppio tocco',
        'Passaggio a scavalcare',
        'Passaggio calibrato'
    ])
    player.special_skills.scoring = any(x in special_skills for x in [
        'Finalizzazione acrobatica',
        'Opportunista',
        'Tiro di collo',
        'Tiro di prima'
    ])
    player.special_skills.one_on_one_shot = any(x in special_skills for x in [
        'Pallonetto mirato',
        'Rapace dell\'area',
        'Rimbalzo interno'
    ])
    player.special_skills.post_player = 'Collante' in special_skills
    player.special_skills.df_positioning = 'Sviluppo' in special_skills
    player.special_skills.long_shots = any(x in special_skills for x in [
        'Tiratore',
        'Tiri a salire',
        'Tiri a scendere',
        'Tiro da lontano'
    ])
    player.special_skills.side = any(x in special_skills for x in [
        'Ala prolifica',
        'Cross calibrato',
        'Specialista dei cross'
    ])
    player.special_skills.one_on_one_stopper = 'Portiere difensivo' in special_skills
    player.special_skills.penalty_stopper = 'Para-rigori' in special_skills
    player.special_skills.dc_com = any(x in special_skills for x in [
        'Disimpegno acrobatico',
        'Intercettazione'
    ])
    player.special_skills.covering = 'Tornante' in special_skills
    player.special_skills.sliding = 'Spirito combattivo' in special_skills
    player.special_skills.marking = any(x in special_skills for x in [
        'Colpo di testa',
        'Marcatore'
    ])
    player.special_skills.outside_kick = any(x in special_skills for x in [
        'Esterno a giro',
        'Tiri a salire',
        'Tiri a scendere'
    ])
    player.special_skills.one_touch_pass = any(x in special_skills for x in [
        'Colpo di tacco',
        'Passaggio di prima'
    ])
    player.special_skills.long_throw = any(x in special_skills for x in [
        'Rimessa lunga PT',
        'Rimessa profonda PT',
    ])

    # Extra
    player.club = [x.find('td')[1].text for x in info_container if x.find('td', first=True).text == 'Squadra'][0]

    return player


def main():
    session = requests_html.HTMLSession()

    while True:
        s_name = input('Digita il nome del giocatore da aggiornare/inserire oppure EXIT per uscire: ')

        if s_name.lower() == 'exit':
            break

        s_page = session.get(PES_MASTER_URL, params={'q': s_name})
        pl_container = s_page.html.find('.player-card-container', first=True)

        # No results found
        if not pl_container:
            while True:
                x = input('Giocatore non trovato! Aggiungere comunque con impostazioni default? (s/n): ').lower()

                if x in ['s', 'n']:
                    print()
                    break

            if x == 'n':
                print(f'Inserimento del giocatore {s_name} annullato.\n')

            else:
                player = Player()
                player.name = s_name
                player.shirt_name = Player.generate_shirt_name(s_name)
                _id = player.add()
                print(f'{s_name} aggiunto con ID {_id}.\n')

            continue

        # Results found
        figures = pl_container.find('.player-card')
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
            print(f'{str(counter):3} | {player["name"]:20} | {player["ovr"]:2} | {player["pos"]:3} | {player["url"]}')
            counter += 1

        print()

        while True:
            try:
                x = int(
                    input('Inserisci il valore corrispondente al giocatore che vuoi aggiungere (-1 per annullare): ')
                )

                if -1 <= x < len(figures):
                    print()
                    break

            except ValueError:
                pass

        if x == -1:
            continue

        sel_player = players[x]
        pl_page = session.get(sel_player['url'])

        name = get_player_name(pl_page)
        existing_players = Player.from_name(name)

        # No results found
        if len(existing_players) == 0:
            print('Nessun giocatore già presente con nome simile trovato. Il giocatore verrà aggiunto come nuovo.\n')

            while True:
                x = input('Confermi l\'inserimento? (s/n): ').lower()

                if x in ['s', 'n']:
                    print()
                    break

            if x == 's':
                try:
                    player = get_player(pl_page)
                    _id = player.add()
                    print(f'Il giocatore {name} è stato aggiunto correttamente con ID {_id}.\n')
                except Exception as e:
                    print(e.__str__())
                    print('[E0]', f'Si è verificato un errore nell\'inserimento del giocatore {name}.\n')
            else:
                print(f'L\'inserimento del giocatore {name} è stato annullato.\n')

            continue

        # Results found
        print(f'Sono stati trovati {len(existing_players)} giocatori con nome simile: ')

        for i in range(len(existing_players)):
            print(f'{str(i):3} | {str(existing_players[i].id):5} | {existing_players[i].name:30}')

        print()

        while True:
            try:
                sel_player_index = int(input(
                    'Inserisci il valore corrispondente al giocatore da aggiornare (-1 per aggiungerlo, '
                    '-2 per annullare): '
                ))

                if -2 <= sel_player_index < len(existing_players):
                    break
            except ValueError:
                pass

        print()

        if sel_player_index == -2:
            print(f'L\'inserimento del giocatore {name} è stato annullato.\n')
            continue

        while True:
            x = input('Confermi l\'inserimento? (s/n): ').lower()

            if x in ['s', 'n']:
                print()
                break

        if x == 'n':
            print(f'L\'inserimento del giocatore {name} è stato annullato.\n')
            continue

        if sel_player_index == -1:
            try:
                player = get_player(pl_page)
                _id = player.add()
                print(f'Il giocatore {name} è stato aggiunto correttamente con ID {_id}.\n')
            except Exception as e:
                print(e.__str__())
                print('[E1]', f'Si è verificato un errore nell\'inserimento del giocatore {name}.\n')

            continue

        existing_player = existing_players[sel_player_index]

        try:
            player = get_player(pl_page, existing_player)
            _id = player.save()
            print(f'Il giocatore {name} con ID {_id} è stato aggiornato correttamente.\n')
        except Exception as e:
            print(e.__str__())
            print('[E2]', f'Si è verificato un errore nell\'inserimento del giocatore {name}.\n')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e.__str__())
        input('Premi INVIO per terminare')
