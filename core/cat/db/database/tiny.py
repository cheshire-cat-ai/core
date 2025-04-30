from typing import Type, Any
from pydantic import BaseModel

from tinydb import TinyDB, Query
from tinydb.queries import QueryInstance

from cat.utils import singleton
from cat.db.database.abstract import AbstractDatabase
from cat.db.tables import DefaultTable


@singleton
class TinyDatabase(AbstractDatabase):
    """
    TinyDB implementation of AbstractDatabase.
    Provides lightweight, document-oriented storage using JSON files.
    """

    setting_table_class: Type = DefaultTable

    def __init__(self, db_name: str = None, connect: bool = True, *args, **kwargs):
        """
        Initialize TinyDB database.

        Args:
            db_name: Database file name (without extension)
            connect: Whether to connect to database immediately
        """
        super().__init__(db_name=db_name, connect=connect, *args, **kwargs)

        self._setting_table = self.setting_table_class(
            db=self,
            model=self.setting_model_class,
            primary_key=self.setting_primary_key,
            table_name=None
        )

    def get_setting(self):
        """Get settings table from the database"""
        return self._setting_table

    def connect(self):
        """Connect to TinyDB database"""
        self.db = TinyDB(self.db_name or self.get_file_name() + ".json")

    def disconnect(self):
        """Disconnect from TinyDB database"""
        if self.db:
            self.db.close()
            self.db = None

    def _build_query(self, field_name: str, field_value: Any, **kwargs):
        """Build a TinyDB query for field comparison"""
        query = Query()
        return getattr(query, field_name) == field_value

    def _get_table(self, table_name: str, **kwargs):
        """Get a TinyDB table object (or default table if none specified)"""
        if not table_name:
            return self.db
        return self.db.table(table_name)

    def search_query(self, table_name: str, query: Any, first: bool = True, **kwargs):
        """
        Execute a custom query search.

        Args:
            table_name: Name of the table to search
            query: TinyDB QueryInstance to execute
            first: Return only first result if True

        Raises:
            TypeError: If query is not a valid QueryInstance
        """
        if not isinstance(query, QueryInstance):
            raise TypeError("Query must be an instance of Query class.")

        result = self._get_table(table_name).search(query)
        return result[0] if result and first else result

    def select(self, table_name: str, field_name: str, field_value: Any, **kwargs):
        """Select records matching a field value"""
        return self._get_table(table_name).search(self._build_query(field_name, field_value))

    def get_data(self, table_name: str, field_name: str, field_value: Any, **kwargs):
        """Get single record matching a field value or None"""
        result = self.select(table_name=table_name, field_name=field_name, field_value=field_value, **kwargs)
        return result[0] if result else None

    def create_table(self, table_name: str, data: BaseModel, **kwargs):
        """Insert new record into a table"""
        self._get_table(table_name).insert(data.model_dump(mode="json"))

    def drop_table(self, **kwargs):
        """Drop table (not implemented for TinyDB)"""
        pass

    def update_table(self, table_name: str, data: BaseModel, field_name: str, field_value: Any, **kwargs):
        """Update records matching a field value"""
        self._get_table(table_name).update(
            data.model_dump(mode="json"), 
            self._build_query(field_name, field_value)
        )

    def upsert_table(self, table_name: str, data: BaseModel, **kwargs):
        """Insert or update records based on field matching"""
        old_record = self.get_data(table_name=table_name, **kwargs)
        if not old_record:
            self.create_table(table_name=table_name, data=data, **kwargs)
        else:
            self.update_table(table_name=table_name, data=data, **kwargs)

    def delete_table(self, table_name: str, field_name: str, field_value: Any, **kwargs):
        """Delete records matching a field value"""
        self._get_table(table_name).remove(self._build_query(field_name, field_value))

    def all_table(self, table_name: str, **kwargs):
        """Get all records from a table"""
        return self._get_table(table_name).all()
