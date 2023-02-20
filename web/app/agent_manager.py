from typing import Union, List

from langchain.agents import load_tools, initialize_agent
from langchain.agents import Tool, ZeroShotAgent, AgentExecutor
from pprint import pprint


class AgentManager:

    llm = None
    

    @classmethod
    def singleton(cls, llm):

        AgentManager.llm = llm

        # a minimal list of ready available langchain tools/chains. Let's start simple!
        AgentManager.available_tools = [
            "python_repl",
            "requests",
            "terminal",
            "llm-math",
        ]
        # TODO: how to load tools/chains that require configuration or custom classes? Any chain could be loaded
        # TODO: load user created tools/chains, from a folder (like a WP plugin or a Django app)
        
        if not hasattr(cls, '_instance'):
            cls._instance = cls()

        return cls._instance

    
    @classmethod
    def get_agent(cls, tool_list: List[str], return_intermediate_steps=False):
        
        # init agent
        tools = load_tools(tool_list, llm=AgentManager.llm)
        agent = initialize_agent(
            tools,
            AgentManager.llm,
            agent="zero-shot-react-description", # TODO: try out "conversational-react-description"
            verbose=True,
            return_intermediate_steps=return_intermediate_steps
        )
        
        return agent