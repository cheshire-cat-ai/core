from typing import List
from abc import ABC, abstractmethod

from langchain_core.utils import get_colored_text

from cat.utils import BaseModelDict
from cat.log import log

class AgentOutput(BaseModelDict):
    output: str
    intermediate_steps: List = []
    return_direct: bool = False


class BaseAgent:

    @abstractmethod
    async def execute(*args, **kwargs) -> AgentOutput:
        pass

    # TODO: this is here to debug langchain, take it away
    def _log_prompt(self, x):
        # The names are not shown in the chat history log, the model however receives the name correctly
        log.info(
            "The names are not shown in the chat history log, the model however receives the name correctly"
        )
        print("\n", get_colored_text(x.to_string(), "green"))
        return x