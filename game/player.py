
from . import database
from peewee import CharField, BareField

class Player(database.BaseModel):
    email = CharField(unique=True, null=False)
    username = CharField(null=False)
    password_hash = CharField(null=False)
