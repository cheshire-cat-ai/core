from tinydb import TinyDB

from cat.utils import singleton
from cat.env import get_env
from cat.utils import get_base_path


@singleton
class Database:
    def __init__(self):
        self.db = TinyDB(self.get_file_name())

    def get_file_name(self):
        tinydb_file = get_base_path() + "data/metadata.json"
        return tinydb_file


def get_db():
    return Database().db
