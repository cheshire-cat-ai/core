# import re
from copy import copy

from cat.utils import log
from langchain.agents import AgentExecutor, ConversationalAgent
from langchain.chains import LLMChain


class AgentManager:
    def __init__(self, cat):
        self.verbose = cat.verbose
        self.cat = cat

    def get_agent_executor(self):
        mad_hatter = self.cat.mad_hatter

        prompt_prefix = mad_hatter.execute_hook("get_main_prompt_prefix")
        prompt_format_instructions = mad_hatter.execute_hook(
            "get_main_prompt_format_instructions"
        )
        prompt_suffix = mad_hatter.execute_hook("get_main_prompt_suffix")

        # extract automatically input_variables from prompt parts (can't do it yet)
        # full_prompt_content = prompt_prefix + prompt_format_instructions + prompt_suffix
        # input_variables = re.findall(r'\{(.*?)\}', full_prompt_content)
        # input_variables = list(filter(lambda v: ("'" not in v) and ('"' not in v), input_variables)) # avoid problems if prompt contains an example dictionary/JSON
        # log('INPUT VARIABLES')
        # log(input_variables)
        input_variables = [
            "input",
            "chat_history",
            "episodic_memory",
            "declarative_memory",
            "agent_scratchpad",
        ]

        allowed_tools = mad_hatter.execute_hook(
            "get_allowed_tools", copy(mad_hatter.tools)
        )
        allowed_tools_names = [t.name for t in allowed_tools]

        prompt = ConversationalAgent.create_prompt(
            tools=allowed_tools,
            prefix=prompt_prefix,
            format_instructions=prompt_format_instructions,
            suffix=prompt_suffix,
            ai_prefix="AI",
            human_prefix="Human",
            input_variables=input_variables,
        )

        if self.verbose:
            log("Using prompt template:")
            log(prompt.template)

        # main chain
        agent_chain = LLMChain(prompt=prompt, llm=self.cat.llm, verbose=self.verbose)

        # init agent
        agent = ConversationalAgent(
            llm_chain=agent_chain,
            allowed_tools=allowed_tools_names,
            verbose=self.verbose,
        )

        # agent executor
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=allowed_tools,
            return_intermediate_steps=True,
            verbose=self.verbose,
        )

        return agent_executor
