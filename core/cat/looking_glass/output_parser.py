import json
from langchain.agents import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish
from typing import Union

from cat.mad_hatter.mad_hatter import MadHatter
from cat.utils import parse_json
from cat.log import log


class ChooseProcedureOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        log.info(llm_output)

        # Making JSON valid
        llm_output = llm_output.replace("None", "null")

        try:
            parsed_output = parse_json(llm_output)
            parsed_output_log = json.dumps(parsed_output, indent=4)
        except Exception as e:
            log.error(e)
            parsed_output = {}
            parsed_output_log = f"Error during JSON parsing, LLM output was: {llm_output}."

        if not "action" in parsed_output \
            or parsed_output["action"] == "final_answer":
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": None},
                log=parsed_output_log,
            )

        # Extract action
        action = parsed_output["action"]
        if not "action_input" in parsed_output.keys() or parsed_output["action_input"] is None:
            parsed_output["action_input"] = ""
        log.error(parsed_output)
        # Extract action input
        # TODOV2: return proper types (not only strings)
        if isinstance(parsed_output["action_input"], str):
            action_input = parsed_output["action_input"]
        else:
            action_input = json.dumps(parsed_output["action_input"])

        for Form in MadHatter().forms:
            if Form.name == action:
                return AgentFinish(
                    return_values={"output": None, "form": action},
                    log=parsed_output_log,
                )
        log.warning(action_input)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input, log=parsed_output_log)
