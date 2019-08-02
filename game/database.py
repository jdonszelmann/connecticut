import os
import peewee


class BaseModel(peewee.Model):
    class Meta:
        pass

def open_connection(db, drop=False):
    if drop:
        os.remove(db.database)


    try:
        db.connect()
    except peewee.OperationalError:
        print("database was already connected")

    for i in BaseModel.__subclasses__():
        i.bind(db)


    print(f"creating tables {[i.__name__ for i in BaseModel.__subclasses__()]}")
    db.create_tables(BaseModel.__subclasses__(), safe=True)
