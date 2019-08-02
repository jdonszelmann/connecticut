from unittest import TestCase
import game
from test.database import DatabaseTestCase

player1args = {'username' : 'joe', 'email' : 'a@b.c', 'password_hash' : 'AASDF'}
player2args = {'username' : 'jane', 'email' : 'c@b.c', 'password_hash' : 'AAASD'}

class TestGame(DatabaseTestCase):
    def test_create_game(self):
        g = game.Game.create(
            player1=game.Player.create(**player1args),
            player2=game.Player.create(**player2args),
        )
        self.assertGreater(g.identifier, 0)
        self.assertEqual(g.player1.name, "joe")
        self.assertEqual(g.player2.name, "john")

        self.assertGreater(g.player1.identifier, 0)
        self.assertGreater(g.player2.identifier, 0)


    def test_store_game(self):
        g = game.Game.create(
            player1=game.Player.create(**player1args),
            player2=game.Player.create(**player2args),
        )

        try:
            new_g = game.Game.get(game.Game.identifier == g.identifier)
        except game.Game.GameDoesNotExist:
            self.fail() # this entry has to exist

        self.assertEqual(g.identifier, new_g.identifier)

        self.assertEqual(
            new_g.player1.identifier, g.player1.identifier
        )
        self.assertEqual(
            new_g.player2.identifier, g.player2.identifier
        )
