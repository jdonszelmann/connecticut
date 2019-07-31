from unittest import TestCase

from test.database import DatabaseTestCase
import game


class TestConfig(DatabaseTestCase):
    def test_generate_default(self):
        game.Config._overwrite_default_config({
            "a": "b",
            "c": "d"
        })
        game.Config.test_and_generate_default()
        for key, value in game.Config._defaultconfig.items():
            self.assertEqual(game.Config.select().where(game.Config.name == key).get().value, value)

        game.Config._restore()

    def test_test(self):
        game.Config._overwrite_default_config({
            "a": "b",
            "c": "d"
        })
        game.Config.generate_default()
        self.assertFalse(game.Config.test("x"))
        self.assertTrue(game.Config.test("a"))

        self.assertTrue(game.Config.test())

        game.Config._overwrite_default_config({
            "a": "b",
            "c": "d",
            "e": "f"
        })

        self.assertFalse(game.Config.test())

        game.Config._restore()

    def test_test_and_generate_default(self):
        game.Config._overwrite_default_config({
            "a": "b",
            "c": "d"
        })
        game.Config.generate_default()
        self.assertTrue(game.Config.test())

        game.Config._overwrite_default_config({
            "a": "b",
            "c": "d",
            "e": "f"
        })
        game.Config.test_and_generate_default()
        self.assertTrue(game.Config.test("e"))

        game.Config._overwrite_default_config({
            "a": "b",
            "c": "d",
            "e": "h"
        })
        game.Config.test_and_generate_default()

        self.assertEqual(game.Config.get_config_option("e"), "f")

        game.Config._restore()

    def test_get_config_option(self):
        game.Config._overwrite_default_config({
            "a": "b",
        })
        game.Config.generate_default()
        self.assertEqual(game.Config.get_config_option("a"), "b")

        game.Config._restore()
