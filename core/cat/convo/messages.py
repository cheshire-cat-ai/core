import time
from enum import Enum
from typing import List, Optional, Literal, Union

from pydantic import BaseModel, Field, ConfigDict, computed_field

from cat.utils import BaseModelDict, deprecation_warning


class Role(Enum):
    AI = "AI"
    Human = "Human"


class ModelInteraction(BaseModel):
    model_type: Literal["llm", "embedder"]
    source: str
    prompt: str
    input_tokens: int
    started_at: float = Field(default_factory=lambda: time.time())

    model_config = ConfigDict(
        protected_namespaces=()
    )


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

    type: str = "chat"
    user_id: str
    who: str = "AI"
    text: Optional[str] = None
    images: Optional[List[str]] = None
    audio: Optional[List[str]] = None
    why: Optional[MessageWhy] = None

    def __init__(
        self,
        user_id: str,
        content: Optional[str] = None,
        text: Optional[str] = None,
        images: Optional[Union[List[str], str]] = None,
        audio: Optional[Union[List[str], str]] = None,
        why: Optional[MessageWhy] = None,
        who: str = "AI",
        **kwargs,
    ):
        if isinstance(images, str):
            images = [images]

        if isinstance(audio, str):
            audio = [audio]

        super().__init__(user_id=user_id, who=who, content=content, text=text, images=images, audio=audio, why=why, **kwargs)


class UserMessage(BaseModelDict):
    """Class for wrapping user message

    Variables:
        text (str): user message
        user_id (str): user id
    """

    user_id: str
    who: str = "Human"
    text: Optional[str] = None
    images: Optional[List[str]] = None
    audio: Optional[List[str]] = None

    def __init__(
        self,
        user_id: str,
        text: Optional[str] = None,
        images: Optional[Union[List[str], str]] = None,
        audio: Optional[Union[List[str], str]] = None,
        who: str = "Human",
        **kwargs,
    ):
        if isinstance(images, str):
            images = [images]

        if isinstance(audio, str):
            audio = [audio]

        super().__init__(user_id=user_id, who=who, text=text, images=images, audio=audio, **kwargs)

