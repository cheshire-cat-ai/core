from typing import Optional, List, Any, Mapping, Dict
import requests

from langchain_core.language_models.llms import LLM
from langchain_openai.chat_models import ChatOpenAI
from langchain_ollama import ChatOllama



class LLMDefault(LLM):
    @property
    def _llm_type(self):
        return ""

    def _call(self, prompt, stop=None):
        return "You did not configure a Language Model. " "Do it in the settings!"

    async def _acall(self, prompt, stop=None):
        return "You did not configure a Language Model. " "Do it in the settings!"


# elaborated from
# https://python.langchain.com/en/latest/modules/models/llms/examples/custom_llm.html
class LLMCustom(LLM):
    # endpoint where custom LLM service accepts requests
    url: str

    # optional key for authentication
    auth_key: str = ""

    # optional dictionary containing custom configuration
    options: Dict = {}

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        # run_manager: Optional[CallbackManagerForLLMRun] = None,
        run_manager: Optional[Any] = None,
    ) -> str:
        request_body = {
            "text": prompt,
            "auth_key": self.auth_key,
            "options": self.options,
        }

        try:
            response_json = requests.post(self.url, json=request_body).json()
        except Exception as exc:
            raise ValueError(
                "Custom LLM endpoint error " "during http POST request"
            ) from exc

        generated_text = response_json["text"]

        return generated_text

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Identifying parameters."""
        return {"url": self.url, "auth_key": self.auth_key, "options": self.options}


class CustomOpenAI(ChatOpenAI):
    url: str

    def __init__(self, **kwargs):
        super().__init__(model_kwargs={}, base_url=kwargs["url"], **kwargs)


class CustomOllama(ChatOllama):
    def __init__(self, **kwargs: Any) -> None:
        if kwargs["base_url"].endswith("/"):
            kwargs["base_url"] = kwargs["base_url"][:-1]
        super().__init__(**kwargs)
