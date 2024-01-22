from typing import List, Dict
from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class FieldExample:
    user_message: str
    model_before: Dict
    model_after: Dict
    responces: List[str]

class CatForm:  # base model of forms

    model: BaseModel
    start_examples: List[str]
    stop_examples: List[str]
    dialog_examples: List[Dict[str, str]]

    strict: bool = False 
    ask_confirm: bool = False
    return_direct: bool = True

    _autopilot = False

    def __init__(self, cat) -> None:
        self._cat = cat

    def extract(self):
        """
        Update the model and check if user want to continue the form
        """
        pass

    def is_complete() -> bool:
        pass

    def next(self):
        """
        Ask missing informations
        """
        pass

    def submit(self) -> str:
        """
        Action
        """
        raise NotImplementedError

    def clear():
        """
        Clear Form on working memory
        """
        pass

    @property
    def cat(self):
        return self._cat