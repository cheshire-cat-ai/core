from typing import Union, List

from langchain.chains.conversation.memory import ConversationBufferMemory#, ConversationSummaryBufferMemory
from langchain.agents import load_tools, initialize_agent
#from langchain.agents import Tool, ZeroShotAgent, AgentExecutor

from pprint import pprint


class AgentManager:

    llm = None

    def __init__(self, llm=None) -> None:
        AgentManager.llm = llm


    @classmethod
    def singleton(cls, llm):
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
            cls._instance = cls(llm)

        return cls._instance

    
    @classmethod
    def get_agent(cls, tool_list: List[str], return_intermediate_steps=False):
        
        # memory
        # TODO: use also vector memory as context
        #memory = ConversationSummaryBufferMemory(llm=AgentManager.llm, memory_key='chat_history')
        memory = ConversationBufferMemory(memory_key='chat_history')

        # init agent
        tools = load_tools(tool_list, llm=AgentManager.llm)
        agent = initialize_agent(
            tools,
            AgentManager.llm,
            agent="conversational-react-description",
            memory=memory,
            verbose=True,
            #return_intermediate_steps=return_intermediate_steps
        )
        
        return agent