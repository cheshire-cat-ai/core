from typing import Literal, Union

from cat.env import get_env
from cat.db.database.tiny import TinyDatabase
from cat.db.database.sql import SQLDatabase


def get_db(
    type_: Literal["tiny", "sql"] = "sql", 
    *args, 
    **kwargs
) -> Union[TinyDatabase, SQLDatabase]:
    """
    Factory function to get the appropriate database instance.

    Provides a consistent interface to access different database implementations.

    Args:
        type_: The database type to instantiate ("tiny" or "sql")
        *args: Positional arguments to pass to the database constructor
        **kwargs: Keyword arguments to pass to the database constructor

    Returns:
        An instance of the requested database type

    Raises:
        ValueError: When an unsupported database type is specified
    """
    if not type_:
        type_ = get_env("CCAT_DB_TYPE")

    if type_ == "tiny":
        return TinyDatabase(connect=True, *args, **kwargs)

    if type_ == "sql":
        return SQLDatabase(connect=True, *args, **kwargs)

    supported_types = ["tiny", "sql"]
    raise ValueError(
        f"Unsupported database type: {type_}. "
        f"Supported types are {', '.join(supported_types)}."
    )
