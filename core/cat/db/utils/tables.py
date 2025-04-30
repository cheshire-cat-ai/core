from typing import Dict, List, Type, Union, get_args, get_origin
from pydantic import BaseModel
from pydantic_core import PydanticUndefined

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from cat.db.models import SQLBase
from cat.log import log


def build_table(class_: BaseModel, properties: Dict = {}, primary_key_field: str = None, sql_base=SQLBase) -> Type:
    """
    Build a SQLAlchemy table from a Pydantic model.

    This function creates a SQLAlchemy table definition based on a Pydantic model class. It maps Pydantic fields
    to appropriate SQLAlchemy column types, handling basic types and collections.

    Args:
        class_ (BaseModel): The Pydantic model class to convert into a table
        properties (Dict, optional): Additional properties for field mapping. Format: {field_name: {property: value}}
            These properties are passed directly to SQLAlchemy's mapped_column
        primary_key_field (str, optional): Name of the field to be set as primary key

    Returns:
        Type[Base]: A new SQLAlchemy table class inheriting from Base

    Supported type mappings:
        - Basic types (str, int, float, bool): Mapped to corresponding SQLAlchemy types
        - Collections (list, set, dict): Mapped to JSON type
        - Optional types: Supported through Union type checking

    Notes:
        - Table name is derived from the lowercase version of the Pydantic class name
        - Tables are created with extend_existing=True to allow field additions (avoiding conflicts)
        - At least one field must be designated as primary_key=True in properties!
        - Unsupported field types are ignored during mapping
        - Default values and default factories from Pydantic models are preserved

    Examples:
        >>> class User(BaseModel):
        ...     id: int
        ...     name: str
        ...     data: Dict[str, Any]
        ...
        >>> UserTable = build_table(User, {"id": {"primary_key": True}})
    """

    def check_if_type(type_: Type, type_list: List[Type]):
        """Check if the type is in the list of types."""
        for t in type_list:
            if get_origin(type_) == Union:
                # Check Union type arguments
                if t in [get_origin(i_type) or i_type for i_type in get_args(type_)]:
                    return True
            # Check direct type match
            elif type_ is t:
                return True
        return False

    attrs = {
        "__table_args__": {"extend_existing": True},
        "__tablename__": class_.__name__.lower(),
        "__annotations__": {},
        }

    for field_name, field in class_.model_fields.items():
        is_valid = False
        sql_type = None

        # Handle basic types
        if check_if_type(field.annotation, [str, int, float, bool]):
            is_valid = True

            if primary_key_field == field_name:
                if not properties.get(field_name):
                    properties[field_name] = {}
                properties[field_name]["primary_key"] = True

        # Handle collection types
        elif check_if_type(field.annotation, [list, set, dict]):
            sql_type = JSON
            is_valid = True

            if primary_key_field == field_name:
                if not properties.get(field_name):
                    properties[field_name] = {}
                properties[field_name]["primary_key"] = True

        if is_valid:
            attrs["__annotations__"][field_name] = Mapped[field.annotation]

            # Handle default values
            field_default = None
            if field.default is not PydanticUndefined:
                field_default = field.default
            elif field.default_factory is not PydanticUndefined:
                field_default = field.default_factory

            kwargs = {}
            if field_default:
                kwargs["default"] = field_default

            kwargs.update(properties.get(field_name, {}))

            if sql_type:
                attrs[field_name] = mapped_column(sql_type, **kwargs)
            else:
                attrs[field_name] = mapped_column(**kwargs)
        else:
            log.warning(f"{field_name} is not a valid type for SQLAlchemy: {field.annotation}")

    return type(class_.__name__.capitalize(), (sql_base,), attrs)
