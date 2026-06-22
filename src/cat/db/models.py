import os
from uuid import uuid4
import datetime
from piccolo.table import Table
from piccolo.columns import (
    Varchar,
    JSON,
    UUID,
    Timestamptz,
)

from .database import DB


##############################
### globally scoped tables ###
##############################

class KeyValueDB(Table, db=DB):
    """Key Value table to store arbitrary global (installation wide) data."""
    
    key = Varchar(length=1024, primary_key=True)
    value = JSON()
    
    class Meta:
        tablename = "ccat_global_key_value"


##########################
### user scoped tables ###
##########################

class UserKeyValueDB(Table, db=DB):
    """Key Value table to store arbitrary user scoped data.

    Standalone (not a subclass of KeyValueDB): the global table makes `key` its
    primary key, but here the same key must coexist across users, so the key is
    scoped by `user_id`. A surrogate `id` is the primary key; `(user_id, key)`
    uniqueness is enforced in the application layer (UserStore.save upserts).
    """

    id = UUID(primary_key=True, default=uuid4)
    user_id = UUID(index=True)
    key = Varchar(length=1024, index=True)
    value = JSON()

    class Meta:
        tablename = "ccat_user_key_value"

################################################
### utility user scoped table to be extended ###
################################################

class UserScopedDB(Table, db=DB):
    """Abstract user scoped table to be subclassed by plugins."""
    
    id = UUID(primary_key=True, default=uuid4)
    name = Varchar(length=1024)
    updated_at = Timestamptz(
        auto_update=lambda: datetime.datetime.now(datetime.timezone.utc),
        index=True
    )
    user_id = UUID(index=True)

    class Meta:
        abstract = True


def create_tables():
    """Create the core DB tables (idempotent).

    Called during project setup (see `scaffolder.setup_project`), not at import:
    importing this module only declares the tables, it never touches the DB. For
    sqlite, the db directory is created here too, so a fresh project folder gets
    `data/core/core.db` materialized on first setup.
    """
    db_path = getattr(DB, "path", None)
    if db_path:  # sqlite: ensure the db directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    for DBTable in [KeyValueDB, UserKeyValueDB]:
        DBTable.create_table(if_not_exists=True).run_sync()
