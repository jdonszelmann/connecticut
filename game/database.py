import peewee


class BaseModel(peewee.Model):
    class Meta:
        pass

current_database = None
def get_db():
    if current_database is None:
        raise ValueError("Db not initialized yet. Open a connection first.")
    return current_database

def open_connection(db, drop=False):
    # bind every table to this database
    for i in BaseModel.__subclasses__():
        i.bind(db)

    global current_database
    current_database = db

    if drop:
        for i in BaseModel.__subclasses__():
            i.drop_table()
    try:
        db.connect()
    except peewee.OperationalError:
        print("database was already connected")

    print(f"creating tables {[i.__name__ for i in BaseModel.__subclasses__()]}")
    db.create_tables(BaseModel.__subclasses__(), safe=True)
