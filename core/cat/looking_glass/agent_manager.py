import re
import traceback
import json
from copy import copy

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import AgentExecutor, LLMSingleActionAgent, AgentOutputParser

from cat.looking_glass.prompts import ToolPromptTemplate
from cat.looking_glass.output_parser import ToolOutputParser
from cat.log import log


class AgentManager:
    """Manager of Langchain Agent.

    This class manages the Agent that uses the LLM. It takes care of formatting the prompt and filtering the tools
    before feeding them to the Agent. It also instantiates the Langchain Agent.

    Attributes
    ----------
    cat : CheshireCat
        Cheshire Cat instance.

    """
    def __init__(self, cat):
        self.cat = cat


    def execute_tool_agent(self, agent_input, allowed_tools):

        allowed_tools_names = [t.name for t in allowed_tools]

        prompt = ToolPromptTemplate(
            #template= TODO: get from hook,
            tools=allowed_tools,
            # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
            # This includes the `intermediate_steps` variable because it is needed to fill the scratchpad
            input_variables=["input", "intermediate_steps"]
        )

        # main chain
        agent_chain = LLMChain(prompt=prompt, llm=self.cat._llm, verbose=True)

        # init agent
        agent = LLMSingleActionAgent(
            llm_chain=agent_chain,
            output_parser=ToolOutputParser(),
            stop=["\nObservation:"],
            allowed_tools=allowed_tools_names,
            verbose=True
        )

        # agent executor
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=allowed_tools,
            return_intermediate_steps=True,
            verbose=True
        )

        out = agent_executor(agent_input)
        return out
    

    def execute_memory_chain(self, agent_input, prompt_prefix, prompt_suffix):
        
        # memory chain (second step)
        memory_prompt = PromptTemplate(
            template = prompt_prefix + prompt_suffix,
            input_variables=[
                "input",
                "chat_history",
                "episodic_memory",
                "declarative_memory",
            ]
        )

        memory_chain = LLMChain(
            prompt=memory_prompt,
            llm=self.cat._llm,
            verbose=True
        )

        out = memory_chain(agent_input)
        out["output"] = out["text"]
        return out


    def execute_agent(self, agent_input):
        """Instantiate the Agent with tools.

        The method formats the main prompt and gather the allowed tools. It also instantiates a conversational Agent
        from Langchain.

        Returns
        -------
        agent_executor : AgentExecutor
            Instance of the Agent provided with a set of tools.
        """
        mad_hatter = self.cat.mad_hatter

        # this hook allows to reply without executing the agent (for example canned responses, out-of-topic barriers etc.)
        fast_reply = mad_hatter.execute_hook("before_agent_starts", agent_input)
        if fast_reply:
            return fast_reply

        prompt_prefix = mad_hatter.execute_hook("agent_prompt_prefix")
        #prompt_format_instructions = mad_hatter.execute_hook("agent_prompt_instructions")
        prompt_suffix = mad_hatter.execute_hook("agent_prompt_suffix")

        #input_variables = [
        #    "input",
        #    "chat_history",
        #    "episodic_memory",
        #    "declarative_memory",
        #    "agent_scratchpad",
        #]

        #input_variables = mad_hatter.execute_hook("before_agent_creates_prompt", input_variables,
         #                                         " ".join([prompt_prefix, prompt_format_instructions, prompt_suffix]))


        # Try to reply only with tools
        allowed_tools = mad_hatter.execute_hook("agent_allowed_tools")
        tools_are_enough = False
        if len(allowed_tools) > 0:
            try:
                out = self.execute_tool_agent(agent_input, allowed_tools)
                tools_are_enough = out["output"] != None
            except Exception as e:
                error_description = str(e)
                log(error_description, "ERROR") 
                tools_are_enough = False

        # if tools were not enough, use memory # TODO: refine tool output?
        if not tools_are_enough:
            out = self.execute_memory_chain(agent_input, prompt_prefix, prompt_suffix)
        else:
            out["intermediate_steps"] = list(map(lambda x:((x[0].tool, x[0].tool_input), x[1]), out["intermediate_steps"]))

        return out
