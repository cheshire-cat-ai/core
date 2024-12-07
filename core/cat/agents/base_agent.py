from typing import List, Any
from abc import ABC, abstractmethod

from cat.utils import BaseModelDict


class AgentOutput(BaseModelDict):
    output: Any | None = None
    intermediate_steps: List = []
    return_direct: bool = False


class BaseAgent(ABC):

    @abstractmethod
    def execute(*args, **kwargs) -> AgentOutput:
        pass
