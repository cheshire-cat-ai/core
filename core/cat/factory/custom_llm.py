from typing import Optional, List, Any, Mapping, Dict
from langchain.llms.base import LLM


class LLMDefault(LLM):
    @property
    def _llm_type(self):
        return ""

    def _call(self, prompt, stop=None):
        # TODO: if AI prefix in the agent changes, this will break
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
        return "AI: fuuuuuuk"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Identifying parameters."""
        return {
            "url": self.url,
            "auth_key": self.auth_key,
            "options": self.options
        }
