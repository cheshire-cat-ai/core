from typing import List
from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class CatFormConfig:
    # This are only examples of confings, we can define better what is necessary
    intent_examples: List[str]
    strict: bool = False
    return_direct: bool = True


class CatForm:  # base model of forms

    # we can also set config attributes directly in CatForm's subclasses withouth using 
    # a separate config dataclass
    config: CatFormConfig
    model: BaseModel = None

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
        pass

    def clear():
        """
        Clear Form on working memory
        """
        pass

