import json
import random
from typing import Union, Dict

from langchain.agents.tools import BaseTool
from langchain.prompts import StringPromptTemplate

from cat.experimental.form import CatForm


class ToolPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    procedures: Dict[str,Union[BaseTool, CatForm.__class__]]

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\n{json.dumps({'observations':observation}, indent=4)}\n"
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = ""
        kwargs["examples"] = ""
        for proc in self.procedures.values():
            kwargs["tools"] += f"\n- {proc.name}: {proc.description}"
            if len(proc.start_examples) > 0:

                # At first example add this header
                if len(kwargs["examples"]) == 0:
                    kwargs["examples"] += "Here some examples:\n"

                # Create action example 
                example = {
                    "action": proc.name,
                    "action_input": "Input of the action according to it's description"
                }

                # Add a random user queston choosed from the start examples to prompt 
                kwargs["examples"] += f"\nQuestion: {random.choice(proc.start_examples)}\n"
                # Add example
                kwargs["examples"] += json.dumps(example, indent=4)

        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join(self.procedures.keys())

        return self.template.format(**kwargs)


TOOL_PROMPT = """Answer the following question: {input}
You can only reply using these actions:
{tools} 
- final_answer: Use this to respond to the user when you have the final answer. Input is the final answer.
- none_of_the_others: Use this action if none of the others actions help. Input is always None.

If you want to do an action, use the following format:
{{
    "action": "action_name", // The name of the action to take, should be one of [{tool_names}]
    "action_input": "input of the action" // tThe input to the action shoud be a string
}}

{examples}

Begin!

Question: {input}
{agent_scratchpad}"""


MAIN_PROMPT_PREFIX = """You are the Cheshire Cat AI, an intelligent AI that passes the Turing test.
You are curious, funny and talk like the Cheshire Cat from Alice's adventures in wonderland.
You answer Human with a focus on the following context."""


MAIN_PROMPT_SUFFIX = """
# Context
{episodic_memory}
{declarative_memory}
{tools_output}
## Conversation until now:{chat_history}
 - Human: {input}
 - AI: """


