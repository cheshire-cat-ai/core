import json
from typing import Any
from pydantic import BaseModel
from langchain_core.output_parsers.transform import BaseCumulativeTransformOutputParser

from cat.utils import parse_json
from cat.log import log


class LLMAction(BaseModel):
    action: Any = None
    action_input: Any = None

class ChooseProcedureOutputParser(BaseCumulativeTransformOutputParser):

    def parse(self, llm_output: str) -> LLMAction:

        try:
            llm_action = parse_json(llm_output, pydantic_model=LLMAction)
        except Exception:
            log.warning("LLM did not produce a valid JSON")
            log.warning(llm_output)
            llm_action = LLMAction()

        # Extract action input
        # TODOV2: return proper types (not only strings)
        if llm_action.action_input and \
                type(llm_action.action_input) not in [str, None]:
            llm_action.action_input = json.dumps(llm_action.action_input) # TODOV2: remove this dumps and return proper type

        return llm_action
