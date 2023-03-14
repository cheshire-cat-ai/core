from typing import Union, List
from pprint import pprint

from langchain.chains import LLMChain
from langchain.agents import load_tools, Tool, AgentExecutor, ConversationalAgent

from cat.utils import log


class AgentManager:

    def __init__(self, llm, tool_names:List[str]) -> None:
        # a minimal list of ready available langchain tools/chains. Let's start simple!
        self.available_tools = [
            #"python_repl",
            #"requests",
            #"terminal",
            "llm-math",
        ]
        # TODO: how to load tools/chains that require configuration or custom classes? Any chain could be loaded
        # TODO: load user created tools/chains, from a folder (like a WP plugin or a Django app)

        self.llm = llm
        self.tools = None
        self.tool_names_agent = None
        self.set_tools(tool_names)
        
        self.prefix_prompt = '''This is a conversation between a human and an intelligent robot cat that passes the Turing test. The cat is curious and talks like the Cheshire Cat from Alice's adventures in wonderland.

Conversation:
{chat_history}Human: {input}

What would the AI reply? Answer the user needs as best you can, according to the provided recent conversation and relevant context.

Context:
- Things Human said in the past:{episodic_memory}
- Documents containing relevant information:{declarative_memory}

Put particular attention to past conversation and context.
To reply you have access to the following tools:
'''
        self.suffix_prompt = '''{agent_scratchpad}'''
        self.input_variables = [
            'input',
            'chat_history',
            'episodic_memory',
            'declarative_memory',
            'agent_scratchpad'
        ]

   
    def set_tools(self, tool_names:List[str]):

        # tools
        self.tools = load_tools(tool_names, llm=self.llm)
        self.tool_names_agent = [t.name for t in self.tools] # naming is different for th eagent? don't know why

    
    def get_agent_executor(self, return_intermediate_steps:bool=False, prefix_prompt:Union[str,None]=None, suffix_prompt:Union[str,None]=None, input_variables:Union[List[str],None]=None):
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
        if self.tools == None or self.tool_names_agent:
            self.set_tools(self.available_tools)

        # prefix prompt
        if prefix_prompt == None:
            prefix_prompt = self.prefix_prompt

        # suffix prompt
        if suffix_prompt == None:
            suffix_prompt = self.suffix_prompt

        # input_variables
        if input_variables == None:
            input_variables = self.input_variables

        prompt = ConversationalAgent.create_prompt(
            self.tools,
            prefix=prefix_prompt,
            suffix=suffix_prompt,
            input_variables=input_variables,
        )

        log('Using prompt template:')
        log(prompt.template)

        # main chain
        chain = LLMChain(
            prompt=prompt,
            llm=self.llm,
            verbose=True
        )

        # init agent
        agent = ConversationalAgent(
            llm_chain=chain,
            allowed_tools=self.tool_names_agent,
            verbose=True
        )

        # agent executor
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            return_intermediate_steps=return_intermediate_steps,
            verbose=True
        )
        
        return agent_executor