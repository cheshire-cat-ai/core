from abc import ABC, abstractmethod
from typing import Any, Dict, Type

from cat.db.models import Setting

from cat.db.tables.default import DefaultTable


class AbstractDatabase(ABC):
    """
    Abstract class for database operations.
    """

    settings_table_class: Type = ...
    settings_model_class: Type = Setting
    settings_primary_key: str = "setting_id"

    def __init__(self, db_name: str, connect: bool = False):
        self.db_name = db_name
        self.db = None

        if connect:
            self.connect()

    # Database connection
    @abstractmethod
    def connect(self):
        """
        Connect to the database.
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnect from the database.
        """
        pass


    # Settings table
    @abstractmethod
    def get_settings(self):
        """
        Get settings from the database.
        """
        pass

    @property
    def settings(self) -> "DefaultTable":
        """
        Get settings from the database.
        """
        return self.get_settings()


    # Database operations
    @abstractmethod
    def select(self, model: Type, table_name: str, data: Dict | Type = None, **kwargs):
        """
        Select data from the database.
        """
        pass

    @abstractmethod
    def search_query(self, model: Type, table_name: str, query: Any = None, first: bool = True, **kwargs):
        """
        Search for a specific query in the database.
        """
        pass

    @abstractmethod
    def get_data(self, model: Type, table_name: str, data: Dict | Type = None, **kwargs):
        """
        Get data from the database or None.
        """
        pass

    @abstractmethod
    def create_table(self, model: Type, table_name: str, data: Dict | Type = None, **kwargs):
        """
        Create a table in the database.
        """
        pass

    @abstractmethod
    def drop_table(self, model: Type, table_name: str):
        """
        Drop the existing table.
        """
        pass

    @abstractmethod
    def update_table(self, model: Type, table_name: str, data: Dict | Type = None, **kwargs):
        """
        Update data in the table.
        """
        pass

    @abstractmethod
    def upsert_table(self, model: Type, table_name: str, data: Dict = None, **kwargs):
        """
        Upsert data in the table.
        """
        pass

    @abstractmethod
    def delete_table(self, model: Type, table_name: str, data: Dict | Type = None, **kwargs):
        """
        Delete data from the table.
        """
        pass

    @abstractmethod
    def all_table(self, model: Type, table_name: str):
        """
        Get all data from the table.
        """
        pass
