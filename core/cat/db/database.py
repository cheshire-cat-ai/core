from tinydb import TinyDB

#TODO can we add a verbose level for logging?

class Database:

    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.db = TinyDB(cls._instance.get_file_name())
        return cls._instance.db
    
    def get_file_name(self):
        return "metadata.json"
    


def get_db():
    return Database()