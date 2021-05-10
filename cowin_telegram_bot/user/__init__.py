from peewee import SqliteDatabase, Model, TextField, IntegerField, BooleanField

sqlite_db = SqliteDatabase("database.db", pragmas={"journal_mode": "wal"})


class BaseModel(Model):
    """A base model that will use our Sqlite database."""

    class Meta:
        database = sqlite_db


class User(BaseModel):
    id = IntegerField()
    pincode = IntegerField()
    notify = BooleanField()
    first_name = TextField()
    last_name = TextField()
    created_at = TextField()
    deleted_at = TextField()
    min_age_limit = IntegerField()
