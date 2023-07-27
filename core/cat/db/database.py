from tinydb import TinyDB
import os

#TODO can we add a verbose level for logging?

class Database:

    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.db = TinyDB(cls._instance.get_file_name())
        return cls._instance.db

    def get_file_name(self):
        tinydb_file = os.getenv("METADATA_FILE", "metadata.json")
        return tinydb_file

def get_db():
    return Database()