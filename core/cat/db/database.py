from tinydb import TinyDB

#TODO can we add a verbose level for logging?

class Database:
    _instance = None
    def __new__(cls):
        if not cls._istance:
            cls._instance = super().__new__(cls)
            cls._instance.db = TinyDB("metadata.json")
        return cls._instance.db