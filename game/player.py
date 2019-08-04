
from . import database
from peewee import CharField, AutoField, ForeignKeyField

class Player(database.BaseModel):
    email = CharField(unique=True, null=False)
    username = CharField(null=False)
    password_hash = CharField(null=False)

    def in_game(self, game):
        return game.id in (i.id for i in zip(self.games1, self.games2))


