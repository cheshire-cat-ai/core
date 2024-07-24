import json
from typing import Union, Dict
from pydantic import BaseModel
from langchain_core.output_parsers.transform import BaseCumulativeTransformOutputParser

from cat.mad_hatter.mad_hatter import MadHatter
from cat.utils import parse_json
from cat.log import log


class LLMAction(BaseModel):
    action: Union[str, None] = None
    action_input: Union[str, None] = None

class ChooseProcedureOutputParser(BaseCumulativeTransformOutputParser):

    def parse(self, llm_output: str) -> LLMAction:

        try:
            llm_action = parse_json(llm_output, pydantic_model=LLMAction)
        except Exception as e:
            log.error(e)
            llm_action = LLMAction()

        # Extract action input
        # TODOV2: return proper types (not only strings)
        if llm_action.action_input and \
                not isinstance(llm_action.action_input, str):
            llm_action.action_input = json.dumps(llm_action.action_input)

        return llm_action
