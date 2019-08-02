import game
from test.database import DatabaseTestCase

player1args = {'username' : 'joe', 'email' : 'a@b.c', 'password_hash' : 'AASDF'}
player2args = {'username' : 'jane', 'email' : 'c@b.c', 'password_hash' : 'AAASD'}

class TestEngine(DatabaseTestCase):
    def test_place_piece(self):
        g = game.Game.create_default(
            player1=game.Player.create(**player1args),
            player2=game.Player.create(**player2args),
        )

        g.set_piece(6, 6)
        g.switch_player()
        for x, y in g.get_available():
            g.set_piece(x, y)

        print(g)
