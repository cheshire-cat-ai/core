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

class UserKeyValueDB(KeyValueDB, db=DB):
    """Key Value table to store arbitrary user scoped data."""
    
    user_id = UUID(index=True)
    
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


# Init DB tables
for DBTable in [KeyValueDB, UserKeyValueDB]:
    DBTable.create_table(if_not_exists=True).run_sync()
