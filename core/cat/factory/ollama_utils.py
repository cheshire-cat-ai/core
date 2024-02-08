from typing import Any, Optional, List, Iterator, AsyncIterator, Type

import requests
from cat.mad_hatter.decorators import tool, hook, plugin
import aiohttp
import langchain.llms.ollama

from pydantic import ConfigDict

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
            raise OllamaEndpointNotFoundError(  # noqa: F821
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
                    raise OllamaEndpointNotFoundError( # noqa: F821
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