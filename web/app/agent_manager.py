from typing import Union, List
from pprint import pprint

from langchain.chains import LLMChain
from langchain.agents import load_tools, Tool, AgentExecutor, ConversationalAgent

from .utils import log


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
    def get_agent_executor(cls, tool_names: List[str], return_intermediate_steps=False):


        # tools
        tools = load_tools(tool_names, llm=AgentManager.llm)
        tool_names_agent = [t.name for t in tools] # naming is different for th eagent? don't know why


        # main prompt
        prefix = '''This is a conversation between a human and an intelligent robot cat that passes the Turing test. The cat is curious and talks like the Cheshire Cat from Alice's adventures in wonderland.

Conversation:
{chat_history}Human: {input}

What would the AI reply? Answer the user needs as best you can, according to the provided recent conversation and relevant context.

Context:
- Things Human said in the past:{episodic_memory}
- Documents containing relevant information:{declarative_memory}

Put particular attention to past conversation and context.
To reply you have access to the following tools:
'''

        suffix = '''{agent_scratchpad}'''

        prompt = ConversationalAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=[
                'input',
                'chat_history',
                'episodic_memory',
                'declarative_memory',
                'agent_scratchpad'
            ],
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
            allowed_tools=tool_names_agent,
            verbose=True
        )

        # agent executor
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            return_intermediate_steps=return_intermediate_steps,
            verbose=True
        )
        
        return agent_executor