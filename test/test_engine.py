import game
from test.database import DatabaseTestCase
from game.piece import Piece

player1args = {'username' : 'joe', 'email' : 'a@b.c', 'password_hash' : 'AASDF'}
player2args = {'username' : 'jane', 'email' : 'c@b.c', 'password_hash' : 'AAASD'}

class TestEngine(DatabaseTestCase):
    def test_get_all_pieces(self):
        player1=game.Player.create(**player1args)
        player2=game.Player.create(**player2args)

        g = game.Game.create_default(
            player1=player1,
            player2=player2,
        )


        g.set_piece(0, 1)
        g.set_piece(0, 3)
        g.set_piece(0, 5)
        g.set_piece(0, 7)

        self.assertEqual(len(list(g.get_all_pieces())), 4)

    def test_set_piece(self):
        player1=game.Player.create(**player1args)
        player2=game.Player.create(**player2args)

        g = game.Game.create_default(
            player1=player1,
            player2=player2,
        )


        g.set_piece(0, 1)
        g.set_piece(0, 3)
        g.set_piece(0, 5)
        g.set_piece(0, 7)


    def test_get_piece1(self):
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

        self.assertEqual(len(list(g.get_all_pieces())), 0)

        piece = g.set_piece(0, 1)
        self.assertEqual(len(list(g.get_all_pieces())), 1)

        for i in range(g.width):
            for j in range(g.height):
                p = g.get_piece(i,j)
                if i == 0 and j == 1:
                    self.assertNotEqual(p, None)
                    self.assertEqual(piece.id, p.id)
                else:
                    self.assertEqual(p, None)



    def test_get_piece2(self):
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
                piece = g.set_piece(i, j)
                player = g.who.id
                newpiece = g.get_piece(i, j)

                self.assertNotEqual(newpiece, None)
                self.assertEqual(newpiece.player.id, player)
                self.assertEqual(piece.id, newpiece.id)


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

    def test_out_of_bounds(self):
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

        self.assertIsNone(g.set_piece(-1, 0))
        self.assertIsNone(g.set_piece(0, -1))
        self.assertIsNone(g.set_piece(-1, -1))
        self.assertIsNone(g.set_piece(100, 0))
        self.assertIsNone(g.set_piece(0, 100))
        self.assertIsNone(g.set_piece(100, 100))
        self.assertIsNone(g.set_piece(-1, 100))

        self.assertIsNotNone(g.set_piece(1, 0))

        # in the center of the board, so shouldn't be placed
        self.assertIsNone(g.set_piece(10, 10))

    def test_cascade_remove_pieces(self):
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

        g.set_piece(0, 2)
        g.switch_player()
        g.set_piece(0, 4)
        g.switch_player()
        id_should_be_removed = int(g.set_piece(1, 4).id)
        g.switch_player()
        g.set_piece(0, 0)
        g.switch_player()
        g.set_piece(12, 12)
        g.switch_player()
        g.set_piece(1, 2)

        print(g)

        self.assertIsNone(Piece.get_or_none(Piece.id == id_should_be_removed))

