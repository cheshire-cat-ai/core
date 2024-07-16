from typing import Any, Dict, List
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.outputs.llm_result import LLMResult
import tiktoken
from cat.convo.messages import LLMModelInteraction
import time


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
            LLMModelInteraction(
                source=source,
                prompt="",
                reply="",
                input_tokens=0,
                output_tokens=0,
                ended_at=0,
            )
        )

    def _count_tokens(self, text: str) -> int:
        # cl100k_base is the most common encoding for OpenAI models such as GPT-3.5, GPT-4 - what about other providers?
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        input_tokens = sum(self._count_tokens(prompt) for prompt in prompts)
        self.last_interaction.prompt = ''.join(prompts)
        self.last_interaction.input_tokens = input_tokens

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        self.last_interaction.output_tokens = self._count_tokens(response.generations[0][0].text)
        self.last_interaction.reply = response.generations[0][0].text
        self.last_interaction.ended_at = time.time()

    @property
    def last_interaction(self) -> LLMModelInteraction:
        return self.stray.working_memory.model_interactions[-1]
