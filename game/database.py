import peewee


class BaseModel(peewee.Model):
    class Meta:
        pass

def open_connection(db, drop=False):
    for i in BaseModel.__subclasses__():
        i.bind(db)


    if drop:
        for i in BaseModel.__subclasses__():
            i.drop_table()

    try:
        db.connect()
    except peewee.OperationalError:
        print("database was already connected")

    print(f"creating tables {[i.__name__ for i in BaseModel.__subclasses__()]}")
    db.create_tables(BaseModel.__subclasses__(), safe=True)
