import time

from typing import List, Type, Dict
from pydantic import ConfigDict

from langchain.llms.base import LLM

from cat.mad_hatter.decorators import hook
from cat.factory.llm import LLMSettings


# canned responses for the fake LLM
fake_responses_map = {
    "hey": "bla bla bla",
}


# langchin FakeLLMs only support lists
# https://api.python.langchain.com/en/latest/_modules/langchain_community/llms/fake.html
class FakeTestLLM(LLM):

    responses: Dict = fake_responses_map

    @property
    def _llm_type(self):
        return "fake"

    def _call(self, prompt: str, stop=None) -> str:
        """Return mapped response"""
        return self.responses.get(
            prompt,
            "No reply available in FakeTestLLM."
        )
    
    async def _acall(self, prompt: str, stop=None) -> str:
        return self._call(prompt)


class FakeTestLLMConfig(LLMSettings):
    """Fake LLM for testing purposes."""

    _pyclass: Type = FakeTestLLM

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Fake LLM",
            "description": "Fake LLM for testing purposes",
            "link": "",
        }
    )

@hook
def factory_allowed_llms(allowed, cat) -> List:
    allowed.append(FakeTestLLMConfig)
    return allowed