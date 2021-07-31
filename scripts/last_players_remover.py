from classes.Player import Player


def main():
    x = int(input('Inserisci il numero di giocatori da rimuovere (Verranno rimossi gli ultimi n giocatori): '))
    Player.remove_last(x)
    print(f'\nGli ultimi {x} giocatori sono stati rimossi.')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e.__str__())
        input('Premi INVIO per terminare.')
