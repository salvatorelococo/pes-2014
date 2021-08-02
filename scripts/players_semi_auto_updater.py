from classes.Team import Club


def main(starting_club_id: int = 67):
    clubs = Club.get_all()

    for club in clubs[starting_club_id - 67:]:
        print()
        print(f'{club.id:3} {club.name}')
        players = club.get_players()

        for player in players[:]:
            try:
                print(player, 'aggiornato!' if player.update() else 'non aggiornato!')
            except Exception as e:
                print(player)
                raise e


if __name__ == '__main__':
    main()
