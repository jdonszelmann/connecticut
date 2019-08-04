# coding=utf-8
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

        return cls.create(*args, width=width, height=height, name=name, who=who, **kwargs)

    def start(self):
        pass

    def __str__(self):
        if self.width > 26:
            raise ValueError("Width of Field cannot exceed 26.")

        if self.height > 99:
            raise ValueError("Height of Field cannot exceed 99.")


        a = ['──'.join([MARKERS[self.piece_player_int(self.get_piece(x, y))]
                        for x in range(self.width)])
             for y in range(self.height - 1, -1, -1)]

        b = ("\n   │%s\n" % ("  │" * (self.width - 1))).join(
            [str(self.height - i - 1).rjust(2) + ' ' + a[i] for i in range(len(a))])
        c = b + "\n " + "".join((str(i).rjust(3) for i in range(self.width)))
        return c

    def place_piece(self, x, y):
        if self.is_legal(x, y):
            piece = self.set_piece(x, y)
            self.switch_player()

            self.save()
            return piece
        return None

    def get_piece(self, x, y):
        from .piece import Piece

        try:
            return (
                Piece.select()
                .join(
                    Game,
                    on=(Piece.game == Game.id)
                ).where(
                    (Piece.x == x) &
                    (Piece.y == y) &
                    (Game.id == self.id)
                ).get()
            )
        except peewee.DoesNotExist:
            return None

    def get_all_pieces(self):
        from .piece import Piece
        try:
            return (i for i in Piece.select().where(
                Piece.game == self
            ))
        except peewee.DoesNotExist:
            return []

    def set_piece(self, x, y):
        from .piece import Piece

        with self.__class__._meta.database.atomic():
            if not (x >= 0 and y >= 0 and x < self.width and y < self.height):
                return None

            self.remove_piece(x, y)
            # get the id of the created piece to later check if it still exists
            retid = int(Piece.create(x=x, y=y, player=self.who, game=self).id)

            try:
                # in_range = (
                #     Piece
                #     .select()
                #     .join(Player, on=(Piece.player == Player.id))
                #     .where(
                #         (
                #             ((Piece.x == x  ) & (Piece.y == y-2)) |
                #             ((Piece.x == x-1) & (Piece.y == y-1)) |
                #             ((Piece.x == x  ) & (Piece.y == y-1)) |
                #             ((Piece.x == x+1) & (Piece.y == y-1)) |
                #             ((Piece.x == x-2) & (Piece.y == y  )) |
                #             ((Piece.x == x-1) & (Piece.y == y  )) |
                #             ((Piece.x == x+1) & (Piece.y == y  )) |
                #             ((Piece.x == x+2) & (Piece.y == y  )) |
                #             ((Piece.x == x-1) & (Piece.y == y+1)) |
                #             ((Piece.x == x  ) & (Piece.y == y+1)) |
                #             ((Piece.x == x+1) & (Piece.y == y+1)) |
                #             ((Piece.x == x  ) & (Piece.y == y+2))
                #
                #           #                     (x, y-2),
                #           #         (x-1, y-1), (x, y-1), (x+1, y-1),
                #           # (x-2, y), (x-1, y),           (x+1, y), (x+2, y),
                #           #         (x-1, y+1), (x, y+1), (x+1, y+1),
                #           #                     (x, y+2),
                #
                #         ) & (Player.id != self.who)
                #     )
                # )

                in_range = (
                    Piece
                        .select()
                        .join(Player, on=(Piece.player == Player.id))
                        .where(
                        (Piece.x >= max(1, x - 2)) &
                        (Piece.x <= min(self.width - 2, x + 3)) &
                        (Piece.y >= max(1, y - 2)) &
                        (Piece.y <= min(self.height - 2, y + 3)) &
                        (Player.id != self.who) &
                        (Piece.game == self.id)
                    )
                )


                checked = []
                for piece in in_range:
                    if not self.is_connected(piece):
                        piece.delete_instance()

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

            # get the created piece from the database. If it doesnt exist anymore, return None
            return Piece.get_or_none(Piece.id == retid)


    def remove_piece(self, x, y):
        from .piece import Piece
        Piece.delete().where((Piece.x == x) & (Piece.y == y)).execute()

    def floodfill(self, piece, pool=None):
        from .piece import Piece
        if pool == None:
            pool = []


        pool.append(piece)
        for px, py in self.get_hooks(piece.x, piece.y):
            hookpiece = self.get_piece(px, py)
            if hookpiece:
                if piece.player == hookpiece.player:
                    if hookpiece not in pool:
                        if self.is_available_from(piece, px, py):
                            pool = self.floodfill(hookpiece, pool)
        return pool

    def get_hooks(self, x, y):
        for m in (-1, 1):
            vx, vy = 1, 2 * m
            for _ in range(4):
                px, py = x + vx, y + vy

                if 0 <= px < self.width and 0 <= py < self.height:
                    yield px, py
                vx, vy = vy, -vx

    def get_available(self):
        from .piece import Piece

        available = set()

        pieces = Piece.select(Piece.x, Piece.y).where(
            (Piece.player == self.who) & \
            (Piece.game == self)
        )

        allpieces = [(p.x, p.y) for p in self.get_all_pieces()]

        for piece in pieces:
            for px, py in self.get_hooks(piece.x, piece.y):
                if (px, py) not in available:
                    if (px, py) not in allpieces:
                        if self.is_available_from(piece, px, py):
                            yield px, py
                            available.add((px, py))

        for y in (0, self.height - 1):
            for x in range(self.width):
                if (x, y) not in available:
                    if (x, y) not in allpieces:
                        yield x, y
                        available.add((x, y))

        for x in (0, self.width - 1):
            for y in range(1, self.height - 1):
                if (x, y) not in available:
                    if (x, y) not in allpieces:
                        yield x, y
                        available.add((x, y))

    def is_available_from(self, piece, hx, hy):
        mx = 1 if hx > piece.x else -1
        my = 1 if hy > piece.y else -1

        detected = 0

        if abs(hy - piece.y) > abs(hx - piece.x):
            for x in range(0, 2):
                for y in range(1 - x, 3 - x):
                    px, py = piece.x + x * mx, piece.y + y * my

                    if self.piece_player_int(self.get_piece(px, py)) == -self.player_int(piece.player):
                        detected += 1
                        break
        else:
            for y in range(0, 2):
                for x in range(1 - y, 3 - y):
                    px, py = piece.x + x * mx, piece.y + y * my

                    if self.piece_player_int(self.get_piece(px, py)) == -self.player_int(piece.player):
                        detected += 1
                        break

        return detected < 2

    def is_connected(self, piece):
        for px, py in self.get_hooks(piece.x, piece.y):
            if self.get_piece(px, py):
                if self.is_available_from(piece, px, py):
                    return True
        return False

    def is_legal(self, x, y):
        return (x, y) in self.get_available()

    def switch_player(self):
        if self.who == self.player1:
            self.who = self.player2
        else:
            self.who = self.player1

    def player_int(self, player):
        if player.id == self.player1.id:
            return 1
        return -1

    def piece_player_int(self, piece):
        if piece:
            return self.player_int(piece.player)
        else:
            return 0

    def other_player(self, player):
        if player.id == self.player1.id:
            return self.player2
        else:
            return self.player1
