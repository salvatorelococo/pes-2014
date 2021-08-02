from os import path

import requests_html

from classes.Player import Player, from_pes_master, get_player_name
from config import FILES_DIR

FILES_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', FILES_DIR, '')

CHARSET = 'utf-8'

PES_MASTER_URL = 'https://www.pesmaster.com/it/pes-2021/'


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
                    player = from_pes_master(pl_page)
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
                player = from_pes_master(pl_page)
                _id = player.add()
                print(f'Il giocatore {name} è stato aggiunto correttamente con ID {_id}.\n')
            except Exception as e:
                print(e.__str__())
                print('[E1]', f'Si è verificato un errore nell\'inserimento del giocatore {name}.\n')

            continue

        existing_player = existing_players[sel_player_index]

        try:
            player = from_pes_master(pl_page, existing_player)
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
