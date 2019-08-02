
from .database import *
from .config import *
from .game import *
from .player import *
from .server import *
from .piece import *

db = peewee.SqliteDatabase("connecticut.db")

def init(db):
    database.open_connection(db)
