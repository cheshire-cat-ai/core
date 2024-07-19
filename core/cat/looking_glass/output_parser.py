import json
from langchain.agents import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish
from typing import Union

from cat.mad_hatter.mad_hatter import MadHatter
from cat.utils import parse_json
from cat.log import log


class ChooseProcedureOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:

        # Making JSON valid
        llm_output = llm_output.replace("None", "null")

        try:
            parsed_output = parse_json(llm_output)
            parsed_output_log = json.dumps(parsed_output, indent=4)
        except Exception as e:
            log.error(e)
            parsed_output = {}
            parsed_output_log = f"Error during JSON parsing, LLM output was: {llm_output}."

        action = parsed_output.get("action", "final_answer")
        action_input = parsed_output.get("action_input", "")
        if action_input is None:
            action_input = ""

        if action == "final_answer":
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": None},
                log=parsed_output_log,
            )

        # Extract action input
        # TODOV2: return proper types (not only strings)
        if not isinstance(action_input, str):
            action_input = json.dumps(action_input)

        for Form in MadHatter().forms:
            if Form.name == action:
                return AgentFinish(
                    return_values={"output": None, "form": action},
                    log=parsed_output_log,
                )

        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input, log=parsed_output_log)
