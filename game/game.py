from . import database
from .player import Player
from .config import Config
from peewee import ForeignKeyField, IntegerField

MARKERS = (
  # unavailable point 0
  "┼",
  # green piece 1
  "\033[1;32mO\033[0m",
  # # point available to green piece 2
  "\033[0;36m┼\033[0m",
  # # point avaibable to both 3/-3
  "\033[1;33m┼\033[0m",
  # # point available to red piece -2
  "\033[0;35m┼\033[0m",
  # red piece -1
  "\033[1;31mO\033[0m"
)

class Game(database.BaseModel):
    player1 = ForeignKeyField(Player, backref="game", null=True)
    player2 = ForeignKeyField(Player, backref="game", null=True)
    width = IntegerField()
    height = IntegerField()
    who = ForeignKeyField(Player, backref='active_games', null=False)

    @classmethod
    def create_default(cls, *args, **kwargs):

        width = int(Config.get_config_option("defaultwidth"))
        height = int(Config.get_config_option("defaultheight"))
        who = kwargs['player1']

        return cls.create(*args, width=width, height=height, who=who, **kwargs)

    def start(self):
        pass

    def __repr__ (self):
        if width > 26:
          raise ValueError("Width of Field cannot exede 26.")

        if height > 99:
          raise ValueError("Height of Field cannot exede 99.")

        a = ['──'.join([MARKERS[self[x, y]] for x in range(self.width)]) for y in range(self.height)]
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
        try:
            return Piece.select().where(
                Piece.x == x and Piece.y == y \
                and Piece.game == self
            ).get()
        except peewee.DoesNotExist:
            return 0

    def set_piece (self, x, y):
        self.remove_piece(x, y)
        Piece.create(x=x, y=y, player=self.who, game=self)

        in_range = Piece.select().where(
            Piece.x >= max(1, x - 2) and \
            Piece.x <= min(self.width - 2, x + 3) and \
            Piece.y >= max(1, y - 2) and \
            Piece.y <= min(self.height - 2, y + 3) and \
            Piece.player != self.who
        ).get()

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

    def removePiece (self, x, y):
        Piece.select().where(Piece.x == x and Piece.y == y).delete_instance().execute()


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
        available = set()

        pieces = Piece.select(Piece.x, Piece.y).where(
            Piece.player == self.player and \
            Piece.game == self
        ).get()

        for piece in pieces:
            for px, py in self.get_hooks(piece.x, piece.y):
                if (px, py) not in available:
                    if self.get_piece(px, py) == 0:
                        if self.is_available_from(piece, px, py):
                            yield px, py
                            available.add((px, py))

            for y in (0, self.game.height - 1):
                for x in range(self.game.width):
                    if (x, y) not in available:
                        if self.getPiece(x, y) == 0:
                            yield x, y
                            available.add((x, y))

            for x in (0, self.game.width - 1):
                for y in range(1, self.game.height - 1):
                    if (x, y) not in available:
                        if self.getPiece(x, y) == 0:
                            yield x, y
                            available.add((x, y))


    def is_available_from (self, piece, hx, hy):
        mx = 1 if x2>x1 else -1
        my = 1 if y2>y1 else -1

        detected = 0

        if abs(hy - piece.y) > abs(hx - piece.x):
            for x in range(0, 2):
                for y in range(1 - x, 3 - x):
                    px, py = piece.x + x * mx, piece.y + y * my

                    if self.get_piece(px, py).player == -piece.player:
                        detected += 1
                        break

        else:
            for y in range(0, 2):
                for x in range(1 - y, 3 - y):
                    px, py = piece.x + x * mx, piece.y + y * my

                    if self.get_piece(px, py).player == -piece.player:
                        detected += 1
                        break

        return detected < 2

    def is_connected (self, piece):
        for px, py in self.get_hooks(piece):
            if self.get_piece(px, py):
                if self.is_available_from(piece, px, py):
                    return True
        return False

    def is_legal (self, x, y):
        return (x, y) in self.get_available()


    def switch_player (self):
        if self.who == self.player1:
            self.who = self.player2
        else:
            self.who = self.player1
