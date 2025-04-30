from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Union
from pathlib import Path

from pydantic import BaseModel

from cat.env import get_env
from cat.db.models import Setting
from cat.db.tables.default import DefaultTable


class AbstractDatabase(ABC):
    """
    Abstract class for database operations.
    Provides a unified interface for different database implementations.
    """

    setting_table_class: Type = ...
    setting_model_class: Type = Setting
    setting_primary_key: str = "name"

    def __init__(self, db_name: str, connect: bool = False):
        """
        Initialize the database connection.

        Args:
            db_name: Name of the database
            connect: Whether to connect immediately
        """
        self.db_name = db_name
        self.db = None

        if connect:
            self.connect()

    def get_file_name(self):
        """Get the file name based on environment configuration"""
        return str(Path(get_env("CCAT_METADATA_FILE")).with_suffix("").absolute())

    def _convert_data_into_table(self, model: Type, data: Union[Dict, BaseModel]) -> Dict:
        """
        Convert data into a format suitable for the table.

        Args:
            data: Input data as dict or Pydantic model
        Returns:
            Data in the format required by the table
        """
        if not data:
            return data

        if isinstance(data, BaseModel):
            return model(**data.model_dump(mode="json"))
        elif isinstance(data, Dict):
            return model(**data)

        return data

    # Database connection methods
    @abstractmethod
    def connect(self):
        """Connect to the database."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from the database."""
        pass

    # Setting table access
    @abstractmethod
    def get_setting(self):
        """Get settings table from the database."""
        pass

    @property
    def setting(self) -> "DefaultTable":
        """Property accessor for database settings."""
        return self.get_setting()

    # Core database operations
    @abstractmethod
    def select(self, model: Type, table_name: str, data: Dict | Type = None, **kwargs):
        """Select data from the database."""
        pass

    @abstractmethod
    def search_query(self, model: Type, table_name: str, query: Any = None, first: bool = True, **kwargs):
        """Execute a specific query in the database."""
        pass

    @abstractmethod
    def get_data(self, model: Type, table_name: str, data: Dict | Type = None, **kwargs):
        """Get a single record from the database or None."""
        pass

    @abstractmethod
    def create_table(self, model: Type, table_name: str, data: Dict | Type = None, **kwargs):
        """Create a table in the database."""
        pass

    @abstractmethod
    def drop_table(self, model: Type, table_name: str):
        """Drop an existing table."""
        pass

    @abstractmethod
    def update_table(self, model: Type, table_name: str, data: Dict | Type = None, **kwargs):
        """Update data in the table."""
        pass

    @abstractmethod
    def upsert_table(self, model: Type, table_name: str, data: Dict = None, **kwargs):
        """Insert or update data in the table."""
        pass

    @abstractmethod
    def delete_table(self, model: Type, table_name: str, data: Dict | Type = None, **kwargs):
        """Delete data from the table."""
        pass

    @abstractmethod
    def all_table(self, model: Type, table_name: str):
        """Get all data from the table."""
        pass
