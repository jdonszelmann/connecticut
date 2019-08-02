import peewee
from .player import Player
from .board import Board
from .database import BaseModel


class Piece(BaseModel):
    x = peewee.IntegerField()
    y = peewee.IntegerField()
    player = peewee.ForeignKeyField(Player, backref="pieces")
    board = peewee.ForeignKeyField(Board, backref="pieces")
