import peewee
from .player import Player
from .database import BaseModel
from .game import Game

class Piece(BaseModel):
    x = peewee.IntegerField(index=True)
    y = peewee.IntegerField(index=True)
    player = peewee.ForeignKeyField(Player, backref="pieces")
    game = peewee.ForeignKeyField(Game, backref="pieces")
