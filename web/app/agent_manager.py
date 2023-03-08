from typing import Union, List
from pprint import pprint

from langchain.chains import LLMChain
from langchain.agents import load_tools, Tool, AgentExecutor, ConversationalAgent

from .utils import log


class AgentManager:

    llm = None
    tools = None
    tool_names_agent = None
    prefix_prompt = '''This is a conversation between a human and an intelligent robot cat that passes the Turing test. The cat is curious and talks like the Cheshire Cat from Alice's adventures in wonderland.

Conversation:
{chat_history}Human: {input}

What would the AI reply? Answer the user needs as best you can, according to the provided recent conversation and relevant context.

Context:
- Things Human said in the past:{episodic_memory}
- Documents containing relevant information:{declarative_memory}

Put particular attention to past conversation and context.
To reply you have access to the following tools:
'''
    suffix_prompt = '''{agent_scratchpad}'''
    input_variables = [
                        'input',
                        'chat_history',
                        'episodic_memory',
                        'declarative_memory',
                        'agent_scratchpad'
                    ]

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
    def set_tools(cls, tool_names: List[str]):

        # tools
        AgentManager.tools = load_tools(tool_names, llm=AgentManager.llm)
        AgentManager.tool_names_agent = [t.name for t in AgentManager.tools] # naming is different for th eagent? don't know why

    
    @classmethod
    def get_agent_executor(cls, return_intermediate_steps:bool=False, prefix_prompt:Union[str,None]=None, suffix_prompt:Union[str,None]=None, input_variables:Union[List[str],None]=None):
        """
        use am.set_tools(['llm-math', 'python_repl']) for set the tools you prefer, if you don't use the set_tools automatically will be setted 
        AgentManager.available_tools = [
            "python_repl",
            "requests",
            "terminal",
            "llm-math",
        ]

        Args:
            return_intermediate_steps (bool, optional): _description_. Defaults to False.
            prefix_prompt (Union[str,None], optional): _description_. Defaults to None.
            suffix_prompt (Union[str,None], optional): _description_. Defaults to None.
            input_variables (Union[List[str],None], optional): _description_. Defaults to None.

        Returns:
            _type_: agent executor
        """
        # set the tools list
        if AgentManager.tools == None or AgentManager.tool_names_agent:
            AgentManager.set_tools(AgentManager.available_tools)

        # prefix prompt
        if prefix_prompt == None:
            prefix_prompt = AgentManager.prefix_prompt

        # suffix prompt
        if suffix_prompt == None:
            suffix_prompt = AgentManager.suffix_prompt

        # input_variables
        if input_variables == None:
            input_variables = AgentManager.input_variables

        prompt = ConversationalAgent.create_prompt(
            AgentManager.tools,
            prefix=prefix_prompt,
            suffix=suffix_prompt,
            input_variables=input_variables,
        )

        log('Using prompt template:')
        log(prompt.template)

        # main chain
        chain = LLMChain(
            prompt=prompt,
            llm=AgentManager.llm,
            verbose=True
        )

        # init agent
        agent = ConversationalAgent(
            llm_chain=chain,
            allowed_tools=AgentManager.tool_names_agent,
            verbose=True
        )

        # agent executor
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=AgentManager.tools,
            return_intermediate_steps=return_intermediate_steps,
            verbose=True
        )
        
        return agent_executor