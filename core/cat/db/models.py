from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field
from typing import Optional, Dict, Union, List


def generate_uuid():
    return str(uuid4())


def generate_timestamp():
    return int(datetime.now().timestamp())


# base class for setting, used to annotate fastAPI endpoints
class SettingBody(BaseModel):
    name: str
    value: Union[Dict, List]
    category: Optional[str] = None


# actual setting class, with additional auto generated id and update time
class Setting(SettingBody):
    setting_id: str = Field(default_factory=generate_uuid)
    updated_at: int = Field(default_factory=generate_timestamp)
