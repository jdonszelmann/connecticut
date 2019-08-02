from unittest import TestCase
import game
from test.database import DatabaseTestCase
import peewee

player1args = {'username' : 'joe', 'email' : 'a@b.c', 'password_hash' : 'AASDF'}
player2args = {'username' : 'jane', 'email' : 'c@b.c', 'password_hash' : 'AAASD'}

class TestGame(DatabaseTestCase):
    def test_create_game(self):
        g = game.Game.create_default(
            player1=game.Player.create(**player1args),
            player2=game.Player.create(**player2args),
        )
        self.assertGreater(g.id, 0)
        self.assertEqual(g.player1.username, "joe")
        self.assertEqual(g.player2.username, "jane")

        self.assertGreater(g.player1.id, 0)
        self.assertGreater(g.player2.id, 0)


    def test_store_game(self):
        g = game.Game.create_default(
            player1=game.Player.create(**player1args),
            player2=game.Player.create(**player2args),
        )

        try:
            new_g = game.Game.get(game.Game.id == g.id)
        except peewee.DoesNotExist:
            self.fail() # this entry has to exist

        self.assertEqual(g.id, new_g.id)

        self.assertEqual(
            new_g.player1.id, g.player1.id
        )
        self.assertEqual(
            new_g.player2.id, g.player2.id
        )
