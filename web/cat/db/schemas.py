# Pydantic models
# Here we create the Pydantic schemas that FastAPI will use to parse and validate the incoming request payloads.

from typing import Union
from datetime import datetime

from pydantic import BaseModel


class SettingBaseSchema(BaseModel):
    setting_id: Union[str, None] = None
    name: str
    value: str
    category: Union[str, None] = None
    enabled: bool = False
    createdAt: Union[datetime, None] = None
    updatedAt: Union[datetime, None] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
