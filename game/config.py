from game.database import BaseModel
from peewee import CharField

class Config(BaseModel):
    name = CharField(unique=True)
    value = CharField()

    _defaultconfig = {
        "defaultwidth" : 13,
        "defaultheight": 13,
        "address": "0.0.0.0",
        "port": "8000"
    }

    # overwrites the default configuration. Watch out with this as it will persist! use cls._restore() to reset it
    @classmethod
    def _overwrite_default_config(cls,cfg):
        if not hasattr(cls, "_olddefaultconfig"):
            cls._olddefaultconfig = cls._defaultconfig
        cls._defaultconfig = cfg

    @classmethod
    def _restore(cls):
        cls._defaultconfig = cls._olddefaultconfig
        delattr(cls, "_olddefaultconfig")

    @classmethod
    def generate_default(cls):
        cls.delete().execute()

        for key, value in cls._defaultconfig.items():
            cls.create(name=key, value=value)

    @classmethod
    def test(cls, value=None):
        if value == None:
            # test if all default keys exist
            for key in cls._defaultconfig.keys():
                if not cls.select().where(cls.name == key).exists():
                    return False
            return True
        else:
            # test if a key exists
            return cls.select().where(cls.name == value).exists()

    @classmethod
    def test_and_generate_default(cls):
        if not cls.test():
            cls.generate_default()

    @classmethod
    def get_config_option(cls, key):
        cls.test_and_generate_default()
        return cls.select().where(cls.name == key).get().value
