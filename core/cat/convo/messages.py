from typing import List, Literal
from cat.utils import BaseModelDict
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from enum import Enum
from pydantic import BaseModel, Field
import time


class Role(Enum):
    AI = "AI"
    Human = "Human"


class ModelInteraction(BaseModel):
    model_type: Literal["llm", "embedder"]
    source: str
    prompt: str
    input_tokens: int
    started_at: float = Field(default_factory=lambda: time.time())


class LLMModelInteraction(ModelInteraction):
    model_type: Literal["llm"] = Field(default="llm")
    reply: str
    output_tokens: int
    ended_at: float


class EmbedderModelInteraction(ModelInteraction):
    model_type: Literal["embedder"] = Field(default="embedder")
    source: str = Field(default="recall")
    reply: List[float]


class MessageWhy(BaseModelDict):
    """Class for wrapping message why

    Variables:
        input (str): input message
        intermediate_steps (List): intermediate steps
        memory (dict): memory
        model_interactions (List[LLMModelInteraction | EmbedderModelInteraction]): model interactions
    """

    input: str
    intermediate_steps: List
    memory: dict
    model_interactions: List[LLMModelInteraction | EmbedderModelInteraction]


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


def convert_to_Langchain_message(
        messages: List[UserMessage | CatMessage],
) -> List[BaseMessage]:
    messages = []
    for m in messages:
        if isinstance(m, CatMessage):
            messages.append(
                HumanMessage(content=m.content, response_metadata={"userId": m.user_id})
            )
        else:
            messages.append(
                AIMessage(content=m.text, response_metadata={"userId": m.user_id})
            )
    return messages


def convert_to_Cat_message(cat_message: AIMessage, why: MessageWhy) -> CatMessage:
    return CatMessage(
        content=cat_message.content,
        user_id=cat_message.response_metadata["userId"],
        why=why,
    )
