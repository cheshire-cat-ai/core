
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field
from typing import Optional, Dict, Union


def generate_uuid():
    return str(uuid4())

def generate_timestamp():
    return int( datetime.now().timestamp() )


class Setting(BaseModel):
    setting_id: str = Field(default_factory=generate_uuid)
    name: str
    value: Dict
    category: Optional[str]
    updated_at: int = Field(default_factory=generate_timestamp)