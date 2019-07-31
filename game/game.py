from . import database
from .player import Player
from .board import Board
from peewee import ForeignKeyField, AutoField


class Game(database.BaseModel):
    identifier = AutoField(primary_key=True)
    player1 = ForeignKeyField(Player, backref="game", null=True)
    player2 = ForeignKeyField(Player, backref="game", null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.board = Board()

    def start(self):
        pass