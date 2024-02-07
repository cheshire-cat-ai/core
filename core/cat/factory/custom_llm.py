import os
from typing import Optional, List, Any, Mapping, Dict, Iterator, AsyncIterator

import aiohttp
import requests

from fastapi import HTTPException

from langchain_core.language_models.llms import LLM
from langchain_openai.llms import OpenAI
from langchain_community.llms.ollama import Ollama, OllamaEndpointNotFoundError

from cat.log import log

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


class CustomOllama(Ollama):
    def __init__(self, **kwargs: Any) -> None:
        if "localhost" in kwargs["base_url"]:
            log.error(
                "you cannot use localhost as host, use instead the machine ip. You can find it by using 'ifconfig' in "
                "linux or 'ipconfig' in windows")
            raise HTTPException(400,
                                "you cannot use localhost as host, use instead the machine ip. You can find it by "
                                "using 'ifconfig' in linux or 'ipconfig' in windows")
        if kwargs["base_url"].endswith("/"):
            kwargs["base_url"] = kwargs["base_url"][:-1]
        super().__init__(**kwargs)

    def _create_stream_patch(
            self,
            api_url: str,
            payload: Any,
            stop: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> Iterator[str]:
        if self.stop is not None and stop is not None:
            raise ValueError("`stop` found in both the input and default params.")
        elif self.stop is not None:
            stop = self.stop

        params = self._default_params

        if "model" in kwargs:
            params["model"] = kwargs["model"]

        if "options" in kwargs:
            params["options"] = kwargs["options"]
        else:
            params["options"] = {
                **params["options"],
                "stop": stop,
                **kwargs,
            }

        if payload.get("messages"):
            request_payload = {"messages": payload.get("messages", []), **params}
        else:
            request_payload = {
                "prompt": payload.get("prompt"),
                "images": payload.get("images", []),
                **params,
            }

        response = requests.post(
            url=api_url,
            headers={
                "Content-Type": "application/json",
            },
            json=request_payload,
            stream=True,
            timeout=self.timeout,
        )
        response.encoding = "utf-8"
        if response.status_code != 200:
            if response.status_code == 404:
                raise OllamaEndpointNotFoundError(
                    "Ollama call failed with status code 404. "
                    "Maybe your model is not found "
                    f"and you should pull the model with `ollama pull {self.model}`."
                )
            else:
                optional_detail = response.json().get("error")
                raise ValueError(
                    f"Ollama call failed with status code {response.status_code}."
                    f" Details: {optional_detail}"
                )
        return response.iter_lines(decode_unicode=True)

    async def _acreate_stream_patch(
            self,
            api_url: str,
            payload: Any,
            stop: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> AsyncIterator[str]:
        if self.stop is not None and stop is not None:
            raise ValueError("`stop` found in both the input and default params.")
        elif self.stop is not None:
            stop = self.stop
        elif stop is None:
            stop = []

        params = self._default_params

        if "model" in kwargs:
            params["model"] = kwargs["model"]

        if "options" in kwargs:
            params["options"] = kwargs["options"]
        else:
            params["options"] = {
                **params["options"],
                "stop": stop,
                **kwargs,
            }

        if payload.get("messages"):
            request_payload = {"messages": payload.get("messages", []), **params}
        else:
            request_payload = {
                "prompt": payload.get("prompt"),
                "images": payload.get("images", []),
                **params,
            }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=api_url,
                    headers={"Content-Type": "application/json"},
                    json=request_payload,
                    timeout=self.timeout,
            ) as response:
                if response.status != 200:
                    if response.status == 404:
                        raise OllamaEndpointNotFoundError(
                            "Ollama call failed with status code 404."
                        )
                    else:
                        optional_detail = await response.json().get("error")
                        raise ValueError(
                            f"Ollama call failed with status code {response.status}."
                            f" Details: {optional_detail}"
                        )
                async for line in response.content:
                    yield line.decode("utf-8")
