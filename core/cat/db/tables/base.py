from typing import Dict, Type, Any, Union
from pydantic import BaseModel

from cat.db.database import abstract as abstract_db


class BaseTable:
    """
    Base class for table operations providing a unified interface
    for different database implementations.
    """

    _is_model_pydantic: bool = False

    def __init__(
            self,
            db: "abstract_db.AbstractDatabase",
            model: Type,
            table_name: str
        ):
        """
        Initialize the table manager.

        Args:
            db: Database connection
            model: Model class for the table
            table_name: Name of the table
        """
        self.table_name = table_name
        self.db = db
        self._model = model

    @property
    def model(self) -> Type:
        """Get the model class for this table."""
        return self._model

    # Database Operations
    def query(self, query: Any, first: bool = True, **kwargs):
        """Execute a custom query against the database."""
        return self.db.search_query(
            model=self._model, 
            table_name=self.table_name, 
            query=query, 
            first=first, 
            **kwargs
        )

    def select(self, data: Dict = None, **kwargs):
        """Select multiple records from the table."""
        return self.db.select(
            model=self._model, 
            table_name=self.table_name, 
            data=data, 
            **kwargs
        )

    def get_data(self, data: Dict = None, first: bool = True, **kwargs):
        """Get data with option to return first result or all."""
        if first:
            return self.db.get_data(
                model=self._model, 
                table_name=self.table_name, 
                data=data,
                **kwargs
            )
        else:
            return self.select(data=data, **kwargs)

    def get_by_attribute(self, first: bool = True, **kwargs):
        """
        Get data by specific attributes.

        Args:
            first: Whether to return only first result
            **kwargs: Attribute filters for the query
        """
        if first:
            return self.db.get_data(
                model=self._model, 
                table_name=self.table_name, 
                **kwargs
            )
        else:
            return self.select(**kwargs)

    def create(self, data=None, **kwargs):
        """Create a new record in the table."""
        return self.db.create_table(
            model=self._model, 
            table_name=self.table_name, 
            data=data, 
            **kwargs
        )

    def drop(self, **kwargs):
        """Drop the entire table."""
        return self.db.drop_table(
            model=self._model, 
            table_name=self.table_name, 
            **kwargs
        )

    def update(self, data: Dict = None, **kwargs):
        """Update an existing record in the table."""
        return self.db.update_table(
            model=self._model, 
            table_name=self.table_name, 
            data=data,
            **kwargs
        )

    def upsert(self, data: Dict = None, **kwargs):
        """Insert new record or update if it exists."""
        return self.db.upsert_table(
            model=self._model, 
            table_name=self.table_name, 
            data=data,
            **kwargs
        )

    def delete(self, data: Dict = None, **kwargs):
        """Delete a record from the table."""
        return self.db.delete_table(
            model=self._model, 
            table_name=self.table_name, 
            data=data, 
            **kwargs
        )

    def all(self, **kwargs):
        """Retrieve all records from the table."""
        return self.db.all_table(
            model=self._model, 
            table_name=self.table_name, 
            **kwargs
        )
