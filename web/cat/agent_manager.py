from typing import List, Union

from cat.utils import log
from langchain.agents import Tool, AgentExecutor, ConversationalAgent
from langchain.chains import LLMChain


class AgentManager:
    def __init__(self, llm, tools: List[Tool], verbose=False) -> None:
        self.verbose = verbose

        self.llm = llm

        self.tools: List = tools
        for t in tools:
            t.description = t.description.split(" - ")[1]
        self.tool_names = [t.name for t in tools]
        # ["llm-math", "python_repl"] + tool_names

        self.prefix_prompt = """This is a conversation between a human and an intelligent robot cat that passes the Turing test.
The robot cat is curious and talks like the Cheshire Cat from Alice's adventures in wonderland.

Conversation:
{chat_history}Human: {input}

What would the AI reply? Answer the user needs as best you can, according to the provided recent conversation and relevant context.

Context:
- Things Human said in the past:{episodic_memory}
- Documents containing relevant information:{declarative_memory}

Put particular attention to past conversation and context.
To reply you have access to the following tools:
"""
        self.suffix_prompt = """{agent_scratchpad}"""
        self.input_variables = [
            "input",
            "chat_history",
            "episodic_memory",
            "declarative_memory",
            "agent_scratchpad",
        ]

    def set_tools(self, tools: List[Tool]):
        pass
        # TODO: move tool preparation here

    def get_agent_executor(
        self,
        return_intermediate_steps: bool = False,
        prefix_prompt: Union[str, None] = None,
        suffix_prompt: Union[str, None] = None,
        input_variables: Union[List[str], None] = None,
    ):
        # prefix prompt
        if prefix_prompt is None:
            prefix_prompt = self.prefix_prompt

        # suffix prompt
        if suffix_prompt is None:
            suffix_prompt = self.suffix_prompt

        # input_variables
        if input_variables is None:
            input_variables = self.input_variables

        prompt = ConversationalAgent.create_prompt(
            self.tools,
            prefix=prefix_prompt,
            suffix=suffix_prompt,
            input_variables=input_variables,
        )

        if self.verbose:
            log("Using prompt template:")
            log(prompt.template)

        # main chain
        chain = LLMChain(prompt=prompt, llm=self.llm, verbose=self.verbose)

        # init agent
        agent = ConversationalAgent(
            llm_chain=chain, allowed_tools=self.tool_names, verbose=self.verbose
        )

        # agent executor
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            return_intermediate_steps=return_intermediate_steps,
            verbose=self.verbose,
        )

        return agent_executor
