import unittest
import game
import peewee
import os

testdbname = "test.db"

class DatabaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        db = peewee.SqliteDatabase(testdbname)
        game.open_connection(db, drop=True)

    def tearDown(self) -> None:
        os.remove(testdbname)
