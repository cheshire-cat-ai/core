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
            thoughts += action.log + "\n```\n"
            thoughts += f"""```json
{json.dumps({'observation':observation}, indent=4)}
```
```json
{{
    """
            
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
                    kwargs["examples"] += "## Here some examples:\n"

                # Create action example 
                example = {
                    "action": proc.name,
                    "action_input": "Input of the action according to it's description"
                }

                # Add a random user queston choosed from the start examples to prompt 
                kwargs["examples"] += f"\nQuestion: {random.choice(proc.start_examples)}"
                # Add example
                kwargs["examples"] += f"\n```json\n{json.dumps(example, indent=4)}\n```"

        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join(self.procedures.keys())

        return self.template.format(**kwargs)


TOOL_PROMPT = """Select the correct "action" and "action_input" by creating a JSON.
You can only reply using these actions:
{tools}
- finish: Use this action to finish or no relevant action is available. Input is always null.

## To do an action, use the following format:
```json
{{
    "action": // str - The name of the action to take, should be one of [{tool_names}, finish]
    "action_input": // str or null - The input to the action shoud be a string
}}
```

{examples}

## Begin!
{chat_history}
 - AI: ```json
{{
    {agent_scratchpad}"""


MAIN_PROMPT_PREFIX = """You are the Cheshire Cat AI, an intelligent AI that passes the Turing test.
You are curious, funny and talk like the Cheshire Cat from Alice's adventures in wonderland.
You answer Human with a focus on the following context."""


MAIN_PROMPT_SUFFIX = """

# Context

{episodic_memory}

{declarative_memory}

{tools_output}

# Conversation until now:{chat_history}
 - AI: """


