import os
from typing import Optional, List, Any, Mapping, Dict
import requests
from langchain.llms.base import LLM
from langchain.llms.openai import OpenAI
from langchain.llms.ollama import Ollama


class LLMDefault(LLM):
    @property
    def _llm_type(self):
        return ""

    def _call(self, prompt, stop=None):
        return "AI: You did not configure a Language Model. " \
               "Do it in the settings!"
    
    async def _acall(self, prompt, stop=None):
        return "AI: You did not configure a Language Model. " \
               "Do it in the settings!"


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
            "options": self.options
        }

        try:
            response_json = requests.post(self.url, json=request_body).json()
        except Exception as exc:
            raise ValueError("Custom LLM endpoint error "
                             "during http POST request") from exc

        generated_text = response_json["text"]

        return generated_text

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Identifying parameters."""
        return {
            "url": self.url,
            "auth_key": self.auth_key,
            "options": self.options
        }


class CustomOpenAI(OpenAI):
    url: str
    
    def __init__(self, **kwargs):
        model_kwargs = {
            'repeat_penalty': kwargs.pop('repeat_penalty'),
            'top_k': kwargs.pop('top_k')
        }
        
        stop = kwargs.pop('stop', None)
        if stop:
            model_kwargs['stop'] = stop.split(',')

        super().__init__(
                    openai_api_key=" ",  
                    model_kwargs=model_kwargs,
                    **kwargs
                )
        
        self.url = kwargs['url']
        self.openai_api_base = os.path.join(self.url, "v1")
