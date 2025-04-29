from typing import Literal

from cat.db.database.abstract import AbstractDatabase
from cat.db.database.tiny import TinyDatabase


def get_db(type_: Literal["tiny", "sqlmodel"] = "tiny", *args, **kwargs) -> AbstractDatabase:
    """
    Get the database instance based on the specified type.

    Args:
        type_ (str): The type of database to use. Can be "tiny" or "sqlmodel".
        *args, **kwargs: Additional arguments to pass to the database instance.
    Returns:
        SQLModelDatabase | TinyDatabase (AbstractDatabase): The database instance.
    """

    if type_ == "tiny":
        return TinyDatabase(connect=True, *args, **kwargs)

    raise ValueError(f"Unsupported database type: {type_}. Supported types are 'tiny' and 'sqlmodel'.")
