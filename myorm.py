import inspect
import sqlite3
from sqlite3 import Error

SQL_TYPES = {
    "CharField": "TEXT",
    "IntegerField": "INTEGER",
    "FloatField": "REAL"
}

# TODO error handling


class Database:
    def __init__(self, db_filename):
        self._db_connection = sqlite3.connect('{}.sqlite3'.format(db_filename))
        self._db_cur = self._db_connection.cursor()

    def query(self, query, params=()):
        with self._db_connection:
            return self._db_cur.execute(query, params)

    def __del__(self):
        self._db_connection.close()


class Model:
    def __init__(self, **kwargs):
        self._data = {
            'id': None
        }

        for key, value in kwargs.items():
            self._data[key] = value

    def __getattribute__(self, key):
        _data = object.__getattribute__(self, '_data')

        if key in _data:
            return _data[key]

        return object.__getattribute__(self, key)

    def __del__(self):
        sql_query = "DELETE FROM {name} WHERE id=?;".format(
            name=self.__class__._get_name()
        )
        self.__class__._db.query(sql_query, [self._data['id']])

    def save(self):
        fields = []
        values = []
        placeholders = []

        for name, field in inspect.getmembers(self.__class__):
            if isinstance(field, (CharField, IntegerField, FloatField)):
                fields.append(name)
                values.append(getattr(self, name))
                placeholders.append('?')

        sql_query = "INSERT INTO {name} ({fields}) VALUES ({placeholders});".format(
            name=self.__class__._get_name(),
            fields=", ".join(fields),
            placeholders=", ".join(placeholders)
        )

        cursor = self.__class__._db.query(sql_query, values)
        self._data['id'] = cursor.lastrowid

    @ classmethod
    def _get_name(cls):
        return cls.__name__.lower()

    @ classmethod
    def create_table(cls, db):
        cls._db = db
        fields = [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT")
        ]

        for name, field in inspect.getmembers(cls):
            if isinstance(field, (CharField, IntegerField, FloatField)):
                fields.append((name, field.sql_type))

        fields = [" ".join(x) for x in fields]
        cls._db.query("CREATE TABLE IF NOT EXISTS {name} ({fields});".format(
            name=cls._get_name(),
            fields=", ".join(fields)
        ))

    @ classmethod
    def filter(cls, **kwargs):
        selectors = []
        values = []
        fields = ['id']

        for key, value in kwargs.items():
            selectors.append((key, "?"))
            values.append(value)

        selectors = ["=".join(x) for x in selectors]

        sql_query = "SELECT * FROM {name} WHERE {selectors};".format(
            name=cls._get_name(),
            selectors=" AND ".join(selectors)
        )

        for name, field in inspect.getmembers(cls):
            if isinstance(field, (CharField, IntegerField, FloatField)):
                fields.append(name)

        result = []
        for item in cls._db.query(sql_query, values).fetchall():
            item_dict = dict(zip(fields, item))
            item_object = cls(**item_dict)
            result.append(item_object)

        return result


class TypeField:
    @ property
    def sql_type(self):
        return SQL_TYPES[self.__class__.__name__]


class CharField(TypeField):
    pass


class IntegerField(TypeField):
    pass


class FloatField(TypeField):
    pass
