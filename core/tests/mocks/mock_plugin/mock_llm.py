
from typing import List, Type
from pydantic import ConfigDict

from langchain_community.chat_models.fake import FakeListChatModel

from cat.mad_hatter.decorators import hook
from cat.factory.llm import LLMSettings

class FakeLLMConfig(LLMSettings):
    """Fake LLM for testing purposes."""

    responses: List[str] = ["I'm a fake LLM!"]
    _pyclass: Type = FakeListChatModel

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Fake LLM",
            "description": "Fake LLM for testing purposes",
            "link": "",
        }
    )

@hook
def factory_allowed_llms(allowed, cat) -> List:
    allowed.append(FakeLLMConfig)
    return allowed
