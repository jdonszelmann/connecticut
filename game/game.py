from . import database
from .player import Player
from .config import Config
from peewee import ForeignKeyField, IntegerField, CharField


class Game(database.BaseModel):
    player1 = ForeignKeyField(Player, backref="games1", null=True)
    player2 = ForeignKeyField(Player, backref="games2", null=True)
    width = IntegerField()
    height = IntegerField()
    name = CharField()

    @classmethod
    def create_default(cls, *args, **kwargs):

        width = int(Config.get_config_option("defaultwidth"))
        height = int(Config.get_config_option("defaultheight"))
        name = Config.get_config_option("defaultname")

        return cls.create(*args, width=width, height=height, name=name, **kwargs)


