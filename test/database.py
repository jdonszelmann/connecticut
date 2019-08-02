import unittest
import game
import peewee
import os

testdbname = "test.db"

class DatabaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        db = peewee.SqliteDatabase(testdbname)
        game.open_connection(db)

    def tearDown(self) -> None:
        os.remove(testdbname)
