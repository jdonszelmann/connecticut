import game
from test.database import DatabaseTestCase
import random

player1args = {'username' : 'joe', 'email' : 'a@b.c', 'password_hash' : 'AASDF'}
player2args = {'username' : 'jane', 'email' : 'c@b.c', 'password_hash' : 'AAASD'}

class TestEngine(DatabaseTestCase):
    def test_place_piece(self):
        pass
        # player1=game.Player.create(**player1args)
        # player2=game.Player.create(**player2args)
        #
        # for _ in range(10):
        #     g = game.Game.create_default(
        #         player1=player1,
        #         player2=player2,
        #     )
        #
        #     rx = random.randint(0, g.width - 1)
        #     ry = random.randint(0, g.height - 1)
        #
        #     g.set_piece(rx, ry)
        #
        #
        #     available = g.get_available()
        #     g.switch_player()
        #
        #     for x, y in available:
        #         g.set_piece(x, y)
        #
        #     print(g, '\n')

    def test_get_piece(self):
        player1 = game.Player.create(**player1args)
        player2 = game.Player.create(**player2args)

        g = game.Game.create(
            player1=player1,
            player2=player2,
            width=13,
            height=13,
            who=player1,
            name="no name"
        )

        for i in range(g.width):
            for j in range(g.height):
                g.set_piece(i, j)
                player = g.who.id
                piece = g.get_piece(i, j)

                self.assertNotEqual(piece, 0)
                self.assertEqual(piece.player.id, player)

    def test_switch_player(self):
        player1 = game.Player.create(**player1args)
        player2 = game.Player.create(**player2args)

        g = game.Game.create(
            player1=player1,
            player2=player2,
            width=13,
            height=13,
            who=player1,
            name="no name"
        )

        player = g.who.id
        g.switch_player()
        self.assertNotEqual(g.who.id, player)
        g.switch_player()
        self.assertEqual(g.who.id, player)
