from typing import Union, List

from langchain.agents import load_tools
from langchain.agents import initialize_agent


class AgentManager:
    """
    me servirebbe una mano a utilizzare agenti langchain a scelta e
    fare in modo che ne siano facilmente agganciati di custom
    """
    llm = None
    
    @classmethod
    def singleton(cls, llm):
        AgentManager.llm = llm
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance



