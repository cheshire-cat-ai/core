from typing import Dict, Type, Any
from pydantic import BaseModel

from cat.db.database import abstract as abstract_db


class BaseTable:
    """
    Table manager for handling settings operations.
    """

    _is_model_pydantic: bool = False

    def __init__(
            self,
            db: "abstract_db.AbstractDatabase",
            model: Type,
            table_name: str
        ):
        self.table_name = table_name
        self.db = db

        self._model = model
        self._check_if_model_is_pydantic()

    @property
    def model(self) -> Type:
        """
        Get the model class for this table.
        """
        return self._model

    @model.setter
    def model(self, value: Type):
        """
        Set the model class for this table.
        """
        self._model = value
        self._check_if_model_is_pydantic()

    def _check_if_model_is_pydantic(self):
        """
        Check if the model is a Pydantic model.
        """
        self._is_model_pydantic = isinstance(self._model, BaseModel)

    # Operations
    def select(self, data: Dict = None, **kwargs):
        """
        Select data from the table.
        """
        return self.db.select(model=self._model, table_name=self.table_name, data=data, **kwargs)
    
    def get_data(self, data: Dict = None, first: bool = True, **kwargs):
        if first:
            return self.db.get_data(model=self._model, table_name=self.table_name, data=data, **kwargs)
        else:
            return self.select(data=data, **kwargs)

    def create(self, data=None, **kwargs):
        return self.db.create_table(model=self._model, table_name=self.table_name, data=data, **kwargs)

    def drop(self, **kwargs):
        """
        Drop the existing table.
        """
        return self.db.drop_table(model=self._model, table_name=self.table_name, **kwargs)

    def update(self, data: Dict = None, **kwargs):
        """
        Update data in the table.
        """
        return self.db.update_table(model=self._model, table_name=self.table_name, data=data, **kwargs)

    def upsert(self, data: Dict = None, **kwargs):
        """
        Upsert data in the table.
        """
        return self.db.upsert_table(model=self._model, table_name=self.table_name, data=data, **kwargs)

    def delete(self, data: Dict = None, **kwargs):
        """
        Delete data from the table.
        """
        return self.db.delete_table(model=self._model, table_name=self.table_name, data=data, **kwargs)

    def get_by_attribute(self, first: bool = True, **kwargs):
        """
        Get data by a specific attribute.
        In kwargs you must provide the attributes that database need to search.
        """

        if first:
            return self.db.get_data(model=self._model, table_name=self.table_name, **kwargs)
        else:
            return self.select(**kwargs)
        
    def query(self, query: Any, first: bool = True, **kwargs):
        """
        Search data in the table.
        Special method for each database.
        """
        return self.db.search_query(model=self._model, table_name=self.table_name, query=query, first=first, **kwargs)

    def all(self, **kwargs):
        """
        Get all data from the table.
        """
        return self.db.all_table(model=self._model, table_name=self.table_name, **kwargs)
