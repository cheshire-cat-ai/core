import json
from langchain.agents import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from typing import Union

from cat.mad_hatter.mad_hatter import MadHatter
from cat.log import log


class ChooseProcedureOutputParser(AgentOutputParser):

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:

        log.debug(llm_output)

        # Maing JSON valid
        llm_output = llm_output.replace("None", "null")
        
        try:
            parsed_output = json.loads("{" + llm_output)
        except Exception as e:
            log.error(e)
            raise OutputParserException(f"Could not parse LLM output: `{llm_output}`")
        
        # Extract action
        action = parsed_output["action"]
        action_input = str(parsed_output["action_input"])

        if action_input:
            action_input = action_input.strip(" ").strip('"')
        else:
            action_input = ""

        if action == "finish":
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": None},
                log=llm_output,
            )

        for Form in MadHatter().forms:
            if Form.name == action:
                return AgentFinish(
                    return_values={
                        "output": None,
                        "form": action
                    },
                    log=llm_output,
                )
            
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input, log=llm_output)