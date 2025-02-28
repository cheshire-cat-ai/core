import time
from typing import Any, Dict, List
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.outputs.llm_result import LLMResult
import tiktoken

from cat.convo.model_interactions import LLMModelInteraction
from cat.log import log


class NewTokenHandler(BaseCallbackHandler):
    def __init__(self, cat):
        # cat could be an instance of CheshireCat or StrayCat
        self.cat = cat

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.cat.send_ws_message(token, msg_type="chat_token")


class ModelInteractionHandler(BaseCallbackHandler):
    """
    Langchain callback handler for tracking model interactions.
    """

    def __init__(self, cat, source: str):
        self.cat = cat
        self.cat.working_memory.model_interactions.append(
            LLMModelInteraction(
                source=source,
                prompt=[],
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

    def on_chat_model_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:

        input_tokens = 0
        input_prompt = []
        # TODOV2: how the hell do we count image tokens?
        # TODOV2: is it a separate count because they have a different pricing?
        # guide here: https://platform.openai.com/docs/guides/vision/calculating-costs#calculating-costs
        messages = prompts[0]
        for m in messages:
            if isinstance(m.content, str):
                input_tokens += self._count_tokens(m.content)
                input_prompt.append(m.content)
            elif isinstance(m.content, list):
                for c in m.content:
                    if c["type"] == "text":
                        input_tokens += self._count_tokens(c["text"])
                        input_prompt.append(c["text"])
                    elif c["type"] == "image_url":
                        # TODOV2: how do we count image tokens?
                        log.warning("Could not count tokens for image message")
                        # do not send back to the client the whole base64 image
                        input_prompt.append("(image, tokens not counted)")
            else:
                log.warning(f"Could not count tokens for message type {c['type']}")

        self.last_interaction.input_tokens = int(input_tokens * 1.2) # You never know
        self.last_interaction.prompt = input_prompt

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        self.last_interaction.output_tokens = self._count_tokens(response.generations[0][0].text)
        self.last_interaction.reply = response.generations[0][0].text
        self.last_interaction.ended_at = time.time()

    @property
    def last_interaction(self) -> LLMModelInteraction:
        return self.cat.working_memory.model_interactions[-1]
