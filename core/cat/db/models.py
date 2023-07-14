
from pydantic import BaseModel
from typing import Optional, Dict, Union

class Setting(BaseModel):
    setting_id: Optional[str]
    name: str
    value: Dict
    category: Optional[str]
    updatedAt: Optional[int] # unix timestamp