
from . import database
from peewee import CharField, AutoField

class Player(database.BaseModel):
    identifier = AutoField(primary_key=True)
    name = CharField(unique=False)

