
from .database import *
from .config import *
from .game import *
from .player import *
from .server import *

db = peewee.SqliteDatabase("connecticut.db")

def init(db):
    database.open_connection(db)

def start():
    init(db)
    #start the ui server
    api = Server().run_in_thread()
