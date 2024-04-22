




from typing import List, Dict
from cat.utils import BaseModelDict

#class WorkingMemory(BaseModelDict):
#    history : List = []


class MessageWhy(BaseModelDict):
    input: str
    intermediate_steps: List
    memory: dict


class CatMessage(BaseModelDict):
    type: str
    content: str
    user_id: str
    why: MessageWhy


class UserMessage(BaseModelDict):
    text: str
    user_id: str

