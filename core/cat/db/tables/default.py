from typing import Any
from pydantic import BaseModel

from cat.db.tables.base import BaseTable
from cat.db.database import abstract as abstract_db


class DefaultTable(BaseTable):
    """
    Table manager for handling settings operations.
    """

    def __init__(
            self,
            db: "abstract_db.AbstractDatabase",
            primary_key: str,
            model: BaseModel,
            table_name: str | None = None,
        ):
        super().__init__(model=model, db=db, table_name=table_name)

        self.primary_key = primary_key


    def get_by_attribute(self, attribute: str, value: Any, first: bool = True):
        """
        Get a setting by a specific attribute.
        """
        kwargs = {
            "field_name": attribute if attribute else self.primary_key,
            "field_value": value
        }

        return super().get_data(first=first, **kwargs)

    def create(self, data: BaseModel):
        super().create(data)

        return self.get_by_attribute(
            attribute=self.primary_key,
            value=getattr(data, self.primary_key)
        )

    def update(self, data: BaseModel, attribute: str = None, value: Any = None):
        super().update(data)

        return self.get_by_attribute(
            attribute=attribute if attribute else self.primary_key,
            value=value or getattr(data, attribute)
        )

    def upsert(self, data: BaseModel, attribute: str = None, value: Any = None):
        attribute = attribute if attribute else self.primary_key

        super().upsert(data,field_name=attribute,field_value=getattr(data, attribute))

        return self.get_by_attribute(
            attribute=attribute,
            value=value or getattr(data, attribute)
        )

    def delete(self, attribute: str = None, value: Any = None):
        return super().delete(
            field_name=attribute if attribute else self.primary_key,
            field_value=value
        )
