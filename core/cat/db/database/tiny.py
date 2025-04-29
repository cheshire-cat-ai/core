from typing import Type, Any
from pydantic import BaseModel

from tinydb import TinyDB, Query
from tinydb.queries import QueryInstance

from cat.env import get_env
from cat.utils import singleton

from cat.db.database.abstract import AbstractDatabase
from cat.db.tables import DefaultTable


@singleton
class TinyDatabase(AbstractDatabase):
    """
    Database manager for handling database operations.
    """

    settings_table_class: Type = DefaultTable


    def __init__(self, db_name: str = None, connect: bool = True, *args, **kwargs):
        super().__init__(db_name=db_name, connect=connect, *args, **kwargs)

        self._settings_table = self.settings_table_class(
            db=self,
            model=self.settings_model_class,
            primary_key=self.settings_primary_key,
            table_name=None
        )

    def get_file_name(self):
        tinydb_file = get_env("CCAT_METADATA_FILE")
        return tinydb_file


    def get_settings(self):
        """
        Get settings from the database.
        """
        return self._settings_table


    def connect(self):
        self.db = TinyDB(self.db_name or self.get_file_name())

    def disconnect(self):
        if self.db:
            self.db.close()
            self.db = None


    def _build_query(self, field_name: str, field_value: Any, **kwargs):
        query = Query()
        return getattr(query, field_name) == field_value

    def _get_table(self, table_name: str, **kwargs):
        if not table_name:
            return self.db

        return self.db.table(table_name)
    

    def search_query(self, table_name: str, query: Any, first: bool = True, **kwargs):
        """
        Search for data in the database.
        """
        if not isinstance(query, QueryInstance):
            raise TypeError("Query must be an instance of Query class.")

        result = self._get_table(table_name).search(query)
        if first:
            return result[0] if result else None
        else:
            return result

    def select(self, table_name: str, field_name: str, field_value: Any, **kwargs):
        """
        Select data from the database.
        """
        return self._get_table(table_name).search(self._build_query(field_name, field_value))

    def get_data(self, table_name: str, field_name: str, field_value: Any, **kwargs):
        """
        Get data from the database.
        """
        result = self.select(table_name=table_name, field_name=field_name, field_value=field_value, **kwargs)

        if len(result) > 0:
            return result[0]
        else:
            return None

    def create_table(self, table_name: str, data: BaseModel,  **kwargs):
        """
        Create a table in the database.
        """
        self._get_table(table_name).insert(data.model_dump(mode="json"))

    def drop_table(self, **kwargs):
        """
        Drop the existing table.
        """
        pass

    def update_table(self, table_name: str, data: BaseModel, field_name: str, field_value: Any, **kwargs):
        """
        Update data in the table.
        """
        self._get_table(table_name).update(data.model_dump(mode="json"), self._build_query(field_name, field_value))

    def upsert_table(self, table_name: str, data: BaseModel, **kwargs):
        """
        Upsert data in the table.
        """
        old_record = self.get_data(table_name=table_name, **kwargs)
        if not old_record:
            self.create_table(table_name=table_name, data=data, **kwargs)
        else:
            self.update_table(table_name=table_name, data=data, **kwargs)

    def delete_table(self, table_name: str, field_name: str, field_value: Any, **kwargs):
        """
        Delete data from the table.
        """
        self._get_table(table_name).remove(self._build_query(field_name, field_value))

    def all_table(self, table_name: str, **kwargs):
        """
        Get all data from the table.
        """
        return self._get_table(table_name).all()
