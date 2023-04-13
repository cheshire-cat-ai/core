from typing import List

from cat.utils import log
from langchain.agents import Tool, AgentExecutor, ConversationalAgent, load_tools
from langchain.chains import LLMChain


class AgentManager:
    def __init__(self, llm, tools: List[Tool], verbose=False):
        self.verbose = verbose
        self.llm = llm
        self.set_tools(tools)

    def set_tools(self, tools: List[Tool]):
        default_tools_name = ["llm-math", "python_repl", "terminal"]
        default_tools = load_tools(default_tools_name, llm=self.llm)

        self.tools = tools + default_tools
        self.tool_names = [t.name for t in self.tools]

    def get_agent_executor(
        self,
        prefix_prompt: str,
        suffix_prompt: str,
        # ai_prefix: str,
        # human_prefix: str,
        input_variables: List[str],
        return_intermediate_steps: bool,
    ):
        prompt = ConversationalAgent.create_prompt(
            self.tools,
            prefix=prefix_prompt,
            suffix=suffix_prompt,
            ai_prefix="AI",
            human_prefix="Human",
            input_variables=input_variables,
        )

        if self.verbose:
            log("Using prompt template:")
            log(prompt.template)

        # main chain
        agent_chain = LLMChain(prompt=prompt, llm=self.llm, verbose=self.verbose)

        # init agent
        agent = ConversationalAgent(
            llm_chain=agent_chain,
            allowed_tools=self.tool_names,
            verbose=self.verbose,
        )

        # agent executor
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            return_intermediate_steps=return_intermediate_steps,
            verbose=self.verbose,
        )

        return agent_executor
