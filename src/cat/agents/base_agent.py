from typing import List
from abc import ABC, abstractmethod


from cat.utils import BaseModelDict

class AgentOutput(BaseModelDict):
    output: str | None = None
    intermediate_steps: List = []
    return_direct: bool = False


class BaseAgent(ABC):

    @abstractmethod
    def execute(*args, **kwargs) -> AgentOutput:
        pass