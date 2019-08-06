import unittest
import game
import peewee
import os
import sys

testdbname = "test.db"

class DatabaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        db = peewee.SqliteDatabase(testdbname)
        game.open_connection(db, drop=True)

    def tearDown(self) -> None:
        if sys.platform == 'linux':
            os.remove(testdbname)
