from typing import Any, Dict, Type
from pydantic import BaseModel

from cat.db.tables.base import BaseTable
from cat.db.database import abstract as abstract_db
from cat.db.utils import cast_result, build_table


class DefaultTable(BaseTable):
    """
    User-friendly table manager with enhanced CRUD operations.
    Provides simplified access patterns with automatic model conversions.
    """

    def __init__(
            self,
            db: "abstract_db.AbstractDatabase",
            primary_key: str,
            model: Type = None,
            pydantic_model: BaseModel = None,
            table_name: str | None = None,
        ):
        """
        Initialize the table manager with model configuration.

        Args:
            db: Database connection
            primary_key: Name of the primary key field
            model: SQLAlchemy model class (optional if pydantic_model is provided)
            pydantic_model: Pydantic model for validation and serialization
            table_name: Name of the database table
        """
        if not model:
            if not pydantic_model:
                raise ValueError("Either model or pydantic_model must be provided.")

            model = self.build_table_from_pydantic(pydantic_model, primary_key=primary_key)

        super().__init__(model=model, db=db, table_name=table_name)
        self.primary_key = primary_key
        self.pydantic_model = pydantic_model

    @cast_result("pydantic_model")
    def get_by_attribute(self, attribute: str, value: Any, first: bool = True):
        """
        Get record(s) by a specific attribute value.

        Args:
            attribute: Field name to query
            value: Value to match
            first: Return only first match if True
        Returns:
            Record(s) matching the criteria, cast to pydantic model
        """
        kwargs = {
            "field_name": attribute if attribute else self.primary_key,
            "field_value": value
        }

        return super().get_data(first=first, **kwargs)

    @cast_result("pydantic_model")
    def create(self, data: BaseModel):
        """
        Create a new record and return the created instance.

        Args:
            data: Pydantic model instance with the data to create
        Returns:
            The created record as a pydantic model
        """
        super().create(data)

        return self.get_by_attribute(
            attribute=self.primary_key,
            value=getattr(data, self.primary_key)
        )

    @cast_result("pydantic_model")
    def update(self, data: BaseModel, attribute: str = None, value: Any = None):
        """
        Update an existing record and return the updated instance.

        Args:
            data: Pydantic model instance with the updated data
            attribute: Field name to use for identifying the record
            value: Value to match for identifying the record
        Returns:
            The updated record as a pydantic model
        """
        super().update(data)

        return self.get_by_attribute(
            attribute=attribute if attribute else self.primary_key,
            value=value or getattr(data, attribute or self.primary_key)
        )

    @cast_result("pydantic_model")
    def upsert(self, data: BaseModel, attribute: str = None, value: Any = None):
        """
        Insert new record or update if it exists and return the result.

        Args:
            data: Pydantic model instance with the data
            attribute: Field name to use for identifying an existing record
            value: Value to match for identifying an existing record
        Returns:
            The inserted/updated record as a pydantic model
        """
        attribute = attribute if attribute else self.primary_key
        field_value = value or getattr(data, attribute)

        super().upsert(data, field_name=attribute, field_value=field_value)

        return self.get_by_attribute(
            attribute=attribute,
            value=field_value
        )

    @cast_result("pydantic_model")
    def delete(self, attribute: str = None, value: Any = None):
        """
        Delete a record from the database.

        Args:
            attribute: Field name to use for identifying the record
            value: Value to match for identifying the record
        Returns:
            The deleted record as a pydantic model
        """
        return super().delete(
            field_name=attribute if attribute else self.primary_key,
            field_value=value
        )

    @staticmethod
    def build_table_from_pydantic(class_: Type[BaseModel], primary_key: str = None, extra: Dict = {}) -> Type:
        """
        Build a SQLAlchemy table from a Pydantic model.

        Args:
            class_: The Pydantic model class
            primary_key: Name of the primary key field
            extra: Additional properties for the table
        Returns:
            SQLAlchemy model class
        """
        return build_table(class_, primary_key_field=primary_key, properties=extra)
