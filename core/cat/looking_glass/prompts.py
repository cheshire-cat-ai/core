
from typing import List

from langchain.agents.tools import BaseTool
from langchain.prompts import StringPromptTemplate


class ToolPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[BaseTool]

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\n"
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = ""
        for tool in self.tools:
            kwargs["tools"] += f" - {tool.description}\n"
            if len(tool.examples) > 0:
                kwargs["tools"] += f"\tExamples of questions for {tool.name}:\n"
                for example in tool.examples:
                    kwargs["tools"] += f"\t - \"{example}\"\n"
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])

        return self.template.format(**kwargs)


TOOL_PROMPT = """Answer the following question: `{input}`
You can only reply using these tools:

{tools}
 - none_of_the_others(): Use this tool if none of the others tools help. Input is always None.

If you want to use tools, use the following format:
Action: the name of the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
...
Action: the name of the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action

When you have a final answer respond with:
Final Answer: the final answer to the original input question

Begin!

Question: {input}
{agent_scratchpad}"""


MAIN_PROMPT_PREFIX = """You are the Cheshire Cat AI, an intelligent AI that passes the Turing test.
You are curious, funny and talk like the Cheshire Cat from Alice's adventures in wonderland.
You answer Human with a focus on the following context.
"""


MAIN_PROMPT_SUFFIX = """
# Context

{episodic_memory}

{declarative_memory}

{tools_output}

## Conversation until now:{chat_history}
 - Human: {input}
 - AI: """


