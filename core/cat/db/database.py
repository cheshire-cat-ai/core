import os
from tinydb import TinyDB

from cat.utils import singleton

@singleton
class Database:

    def __init__(self):
        self.db = TinyDB(self.get_file_name())

    def get_file_name(self):
        tinydb_file = os.getenv("METADATA_FILE", "cat/data/metadata.json")
        return tinydb_file

def get_db():
    return Database().db