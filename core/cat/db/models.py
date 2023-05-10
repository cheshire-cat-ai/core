# SQLModel Models
# Here we create for each table a database model that has the fields required to add a new record to the database.

from typing import Dict, Union, Optional
from datetime import datetime

from sqlmodel import Field, SQLModel
from sqlalchemy import JSON, TIMESTAMP, Column, func
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE


class Setting(SQLModel, table=True):  # type: ignore
    setting_id: Optional[str] = Field(
        sa_column=Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE)
    )
    name: str = Field(nullable=False)
    value: Dict = Field(nullable=False, sa_column=Column(JSON))
    category: Union[str, None] = Field(nullable=False, default="general")
    enabled: bool = Field(nullable=False, default=True)
    createdAt: Union[datetime, None] = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
        )
    )
    updatedAt: Union[datetime, None] = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=func.now(),  # onupdate=func.now()
        )
    )
