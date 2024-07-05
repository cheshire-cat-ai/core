from typing import Any, Dict, List
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.outputs.llm_result import LLMResult
import tiktoken
from cat.log import log
from cat.convo.messages import ModelInteraction

class NewTokenHandler(BaseCallbackHandler):
    def __init__(self, stray):
        # cat could be an instance of CheshireCat or StrayCat
        self.stray = stray

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.stray.send_ws_message(token, msg_type="chat_token")


class ModelInteractionHandler(BaseCallbackHandler):
    """
    Langchain callback handler for tracking model interactions.
    """

    def __init__(self, stray, source: str):
        self.stray = stray
        self.stray.working_memory.model_interactions.append(
            ModelInteraction(
                model_type="llm",
                source=source,
                prompt="",
                reply="",
                input_tokens=0,
                output_tokens=0,
            )
        )


    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        encoding = tiktoken.get_encoding("cl100k_base")
        input_tokens = sum(len(encoding.encode(prompt)) for prompt in prompts)
        self.last_interaction.prompt = ''.join(prompts)
        self.last_interaction.input_tokens = input_tokens

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.last_interaction.output_tokens += 1

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        self.last_interaction.reply = response.generations[0][0].text
    @property
    def last_interaction(self) -> ModelInteraction:
        return self.stray.working_memory.model_interactions[-1]