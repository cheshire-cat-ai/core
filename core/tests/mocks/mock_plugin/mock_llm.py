
from typing import List, Type
from pydantic import ConfigDict

from langchain_community.llms.fake import FakeListLLM

from cat.mad_hatter.decorators import hook
from cat.factory.llm import LLMSettings

class FakeLLMConfig(LLMSettings):
    """Fake LLM for testing purposes."""

    _pyclass: Type = FakeListLLM

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
