from . import database
from .player import Player
from .config import Config
from peewee import ForeignKeyField, IntegerField


class Game(database.BaseModel):
    player1 = ForeignKeyField(Player, backref="round", null=True)
    player2 = ForeignKeyField(Player, backref="round", null=True)
    width = IntegerField()
    height = IntegerField()

    @classmethod
    def create_default(cls, *args, **kwargs):

        width = int(Config.get_config_option("defaultwidth"))
        height = int(Config.get_config_option("defaultheight"))

        return cls.create(*args, width=width, height=height, **kwargs)

    def start(self):
        pass
