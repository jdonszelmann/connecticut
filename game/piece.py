import peewee
from .player import Player
from .database import BaseModel
from .game import Game


class Piece(BaseModel):
    x = peewee.IntegerField()
    y = peewee.IntegerField()
    player = peewee.ForeignKeyField(Player, backref="pieces")
    game = peewee.ForeignKeyField(Game, backref="pieces")
