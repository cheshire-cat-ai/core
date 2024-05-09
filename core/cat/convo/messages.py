from typing import List, Dict
from cat.utils import BaseModelDict
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from enum import Enum


class Role(Enum):
    AI = "AI"
    Human = "Human"

class MessageWhy(BaseModelDict):
    """Class for wrapping message why

    Variables:
        input (str): input message
        intermediate_steps (List): intermediate steps
        memory (dict): memory
    """
    input: str
    intermediate_steps: List
    memory: dict


class CatMessage(BaseModelDict):
    """Class for wrapping cat message

    Variables:
        content (str): cat message
        user_id (str): user id
    """
    content: str
    user_id: str
    type: str = "chat"
    why: MessageWhy | None = None


class UserMessage(BaseModelDict):
    """Class for wrapping user message

    Variables:
        text (str): user message
        user_id (str): user id
    """
    text: str
    user_id: str



def convert_to_Langchain_message(messages: List[UserMessage | CatMessage] ) -> List[BaseMessage]:
    messages = []
    for m in messages:
        if isinstance(m, CatMessage):
            messages.append(HumanMessage(content=m.content, response_metadata={"userId": m.user_id}))
        else:
            messages.append(AIMessage(content=m.text, response_metadata={"userId": m.user_id}))
    return messages

def convert_to_Cat_message(cat_message: AIMessage, why: MessageWhy) -> CatMessage:
    return CatMessage(content=cat_message.content, user_id=cat_message.response_metadata["userId"], why=why)
    

