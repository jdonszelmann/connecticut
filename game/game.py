from . import database
from .player import Player
from .config import Config
import peewee
from peewee import ForeignKeyField, IntegerField, CharField

MARKERS = (
  # unavailable point 0
  "┼",
  # green piece 1
  "O",
  # "\033[1;32mO\033[0m",
  # red piece -1
  "X",
  # "\033[1;31mO\033[0m"
)

class Game(database.BaseModel):
    player1 = ForeignKeyField(Player, backref="games1", null=True)
    player2 = ForeignKeyField(Player, backref="games2", null=True)
    width = IntegerField()
    height = IntegerField()
    name = CharField()
    who = ForeignKeyField(Player, backref='active_games', null=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def create_default(cls, *args, **kwargs):

        width = int(Config.get_config_option("defaultwidth"))
        height = int(Config.get_config_option("defaultheight"))
        who = kwargs['player1']
        name = Config.get_config_option("defaultname")

        return cls.create(*args, width=width, height=height, who=who, **kwargs)

    def start(self):
        pass

    def __str__ (self):
        if self.width > 26:
          raise ValueError("Width of Field cannot exede 26.")

        if self.height > 99:
          raise ValueError("Height of Field cannot exede 99.")

        def piece_to_int (piece):
            if piece == 0:
                return 0
            else:
                return self.player_int(piece.player)

        a = ['──'.join([MARKERS[piece_to_int(self.get_piece(x, y))]
                for x in range(self.width)])
                    for y in range(self.height)]

        b = ("\n   │%s\n" % ("  │" * (self.width - 1))).join([str(self.height - i).rjust(2) + ' ' + a[i] for i in range(len(a))])
        c = b + "\n   " + "  ".join("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:self.width])
        return c


    def place_piece (self, x, y):
        if self.is_legal(x, y):
            self.set_piece(x, y)
            self.switch_player()

            self.save()
            return True
        return False

    def get_piece (self, x, y):
        from .piece import Piece
        try:
            return Piece.select().where(
                Piece.x == x and Piece.y == y \
                and Piece.game == self
            ).get()
        except peewee.DoesNotExist:
            return 0

    def set_piece (self, x, y):
        from .piece import Piece
        self.remove_piece(x, y)
        Piece.create(x=x, y=y, player=self.who, game=self)

        try:
            in_range = Piece.select().where(
                Piece.x >= max(1, x - 2) and \
                Piece.x <= min(self.width - 2, x + 3) and \
                Piece.y >= max(1, y - 2) and \
                Piece.y <= min(self.height - 2, y + 3) and \
                Piece.player.id != self.who.id
            )

            checked = []
            for piece in in_range:
                if not self.is_connected(piece):
                    piece.delete_instance().execute()

                elif piece not in checked:
                    pool = self.floodfill(piece)
                    checked += pool

                    if not any((
                            p.x == 0 or p.x == self.width - 1 \
                            or p.y == 0 or p.y == self.height - 1 \
                            for p in pool)):
                        for p in pool:
                            p.delete_instance()

            self.save()
        except peewee.DoesNotExist:
            pass

    def remove_piece (self, x, y):
        from .piece import Piece
        Piece.delete().where(Piece.x == x and Piece.y == y).execute()

    def floodfill (self, piece, pool=list()):
        pool.append(piece)
        for px, py in self.get_hooks(piece.x, piece.y):
            hookpiece = self.get_piece(px, py)
            if hookpiece:
                if piece.player == hookpiece.player:
                    if hookpiece not in pool:
                        if self.is_available_from(piece, px, py):
                            pool = self.floodfill(hookpiece, pool)
        return pool

    def get_hooks (self, x, y):
        for m in (-1, 1):
            vx, vy = 1, 2 * m
            for _ in range(4):
                px, py = x + vx, y + vy

                if 0 <= px < self.width and 0 <= py < self.height:
                    yield px, py
                vx, vy = vy, -vx

    def get_available (self):
        from .piece import Piece
        available = set()

        pieces = Piece.select(Piece.x, Piece.y).where(
            Piece.player == self.who and \
            Piece.game == self
        )

        for piece in pieces:
            for px, py in self.get_hooks(piece.x, piece.y):
                if (px, py) not in available:
                    if self.get_piece(px, py) == 0:
                        if self.is_available_from(piece, px, py):
                            yield px, py
                            available.add((px, py))

            for y in (0, self.height - 1):
                for x in range(self.width):
                    if (x, y) not in available:
                        if self.get_piece(x, y) == 0:
                            yield x, y
                            available.add((x, y))

            for x in (0, self.width - 1):
                for y in range(1, self.height - 1):
                    if (x, y) not in available:
                        if self.get_piece(x, y) == 0:
                            yield x, y
                            available.add((x, y))

    def is_available_from (self, piece, hx, hy):
        mx = 1 if hx>piece.x else -1
        my = 1 if hy>piece.y else -1

        detected = 0

        if abs(hy - piece.y) > abs(hx - piece.x):
            for x in range(0, 2):
                for y in range(1 - x, 3 - x):
                    px, py = piece.x + x * mx, piece.y + y * my

                    if self.player_int(self.get_piece(px, py).player) == -self.player_int(piece.player):
                        detected += 1
                        break
        else:
            for y in range(0, 2):
                for x in range(1 - y, 3 - y):
                    px, py = piece.x + x * mx, piece.y + y * my

                    if self.player_int(self.get_piece(px, py).player) == -self.player_int(piece.player):
                        detected += 1
                        break

        return detected < 2

    def is_connected (self, piece):
        for px, py in self.get_hooks(piece.x, piece.y):
            if self.get_piece(px, py):
                if self.is_available_from(piece, px, py):
                    return True
        return False

    def is_legal (self, x, y):
        return (x, y) in self.get_available()

    def switch_player (self):
        if self.who.id == self.player1.id:
            self.who = self.player2
        else:
            self.who = self.player1

    def player_int (self, player):
        if player.id == self.player1.id:
            return 1
        return -1
