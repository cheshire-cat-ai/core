"""
This classes are copied from SQLModel 0.0.24 library.
It's not much, but is enough.
"""


from cat.db.utils.sqlmodel.select import select
from cat.db.utils.sqlmodel.session import Session


__all__ = [
    "select",
    "Session",
]