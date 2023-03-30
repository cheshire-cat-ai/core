# SQLModel Models
# Here we create for each table a database model that has the fields required to add a new record to the database.

from datetime import datetime
from typing import Union, Optional

from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE
from sqlalchemy import TIMESTAMP, Column, func
from sqlmodel import Field, SQLModel


class Setting(SQLModel, table=True):
    setting_id: Optional[str] = Field(
        sa_column=Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE)
    )
    name: str = Field(nullable=False)
    value: str = Field(nullable=False)
    category: Union[str, None] = Field(nullable=False)
    enabled: bool = Field(nullable=False, default=True)
    createdAt: Union[datetime, None] = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
        )
    )
    updatedAt: Union[datetime, None] = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
        )
    )
