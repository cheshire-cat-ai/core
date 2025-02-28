"""Various utiles used from the projects."""

import os
import inspect
from datetime import timedelta
from urllib.parse import urlparse
from typing import Dict, Tuple
from pydantic import BaseModel, ConfigDict

from langchain.evaluation import StringDistance, load_evaluator, EvaluatorType
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.utils import get_colored_text

from cat.log import log
from cat.env import get_env


def to_camel_case(text: str) -> str:
    """Format string to camel case.

    Takes a string of words separated by either hyphens or underscores and returns a string of words in camel case.

    Parameters
    ----------
    text : str
        String of hyphens or underscores separated words.

    Returns
    -------
    str
        Camel case formatted string.
    """
    s = text.replace("-", " ").replace("_", " ").capitalize()
    s = s.split()
    if len(text) == 0:
        return text
    return s[0] + "".join(i.capitalize() for i in s[1:])


def verbal_timedelta(td: timedelta) -> str:
    """Convert a timedelta in human form.

    The function takes a timedelta and converts it to a human-readable string format.

    Parameters
    ----------
    td : timedelta
        Difference between two dates.

    Returns
    -------
    str
        Human-readable string of time difference.

    Notes
    -----
    This method is used to give the Language Model information time information about the memories retrieved from
    the vector database.

    Examples
    --------
    >>> print(verbal_timedelta(timedelta(days=2, weeks=1))
    'One week and two days ago'
    """

    if td.days != 0:
        abs_days = abs(td.days)
        if abs_days > 7:
            abs_delta = "{} weeks".format(td.days // 7)
        else:
            abs_delta = "{} days".format(td.days)
    else:
        abs_minutes = abs(td.seconds) // 60
        if abs_minutes > 60:
            abs_delta = "{} hours".format(abs_minutes // 60)
        else:
            abs_delta = "{} minutes".format(abs_minutes)
    if td < timedelta(0):
        return "{} ago".format(abs_delta)
    else:
        return "{} ago".format(abs_delta)


def get_base_url():
    """Allows exposing the base url."""
    secure = "s" if get_env("CCAT_CORE_USE_SECURE_PROTOCOLS") in ("true", "1") else ""
    cat_host = get_env("CCAT_CORE_HOST")
    cat_port = get_env("CCAT_CORE_PORT")
    return f"http{secure}://{cat_host}:{cat_port}/"


def get_base_path():
    """Allows exposing the base path."""
    return "cat/"


def get_plugins_path():
    """Allows exposing the plugins' path."""
    return os.path.join(get_base_path(), "plugins/")


def get_static_url():
    """Allows exposing the static server url."""
    return get_base_url() + "static/"


def get_static_path():
    """Allows exposing the static files' path."""
    return os.path.join(get_base_path(), "static/")


def is_https(url):
    try:
        parsed_url = urlparse(url)
        return parsed_url.scheme == "https"
    except Exception:
        return False


def extract_domain_from_url(url):
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc + parsed_url.path
    except Exception:
        return url


def explicit_error_message(e):
    # add more explicit info on "RateLimitError" by OpenAI, 'cause people can't get it
    error_description = str(e)
    if "billing details" in error_description:
        # happens both when there are no credits or the key is not active
        error_description = """Your OpenAI key is not active or you did not add a payment method.
You need a credit card - and money in it - to use OpenAI api.
HOW TO FIX: go to your OpenAI accont and add a credit card"""

        log.error(
            error_description
        )  # just to make sure the message is read both front and backend

    return error_description


def deprecation_warning(message: str, skip=3):
    """Log a deprecation warning with caller's information.
        "skip" is the number of stack levels to go back to the caller info."""
    
    caller = get_caller_info(skip, return_short=False)

    # Format and log the warning message
    log.warning(
        f"{caller} Deprecation Warning: {message})"
    )


def levenshtein_distance(prediction: str, reference: str) -> int:
    jaro_evaluator = load_evaluator(
        EvaluatorType.STRING_DISTANCE, distance=StringDistance.LEVENSHTEIN
    )
    result = jaro_evaluator.evaluate_strings(
        prediction=prediction,
        reference=reference,
    )
    return result["score"]


def parse_json(json_string: str, pydantic_model: BaseModel = None) -> dict:
    # instantiate parser
    parser = JsonOutputParser(pydantic_object=pydantic_model)

    # clean to help small LLMs
    replaces = {
        "\_": "_",
        "\-": "-",
        "None": "null",
        "{{": "{",
        "}}": "}",
    }
    for k, v in replaces.items():
        json_string = json_string.replace(k, v)

    # first "{" occurrence (required by parser)
    start_index = json_string.index("{")

    # parse
    parsed = parser.parse(json_string[start_index:])
    
    if pydantic_model:
        return pydantic_model(**parsed)
    return parsed


def match_prompt_variables(
        prompt_variables: Dict,
        prompt_template: str
    ) -> Tuple[Dict, str]:
    """Ensure prompt variables and prompt placeholders map, so there are no issues on mismatches"""

    tmp_prompt = PromptTemplate.from_template(
        template=prompt_template
    )

    # outer set difference
    prompt_mismatches = set(prompt_variables.keys()) ^ set(tmp_prompt.input_variables)

    # clean up
    for m in prompt_mismatches:
        if m in prompt_variables.keys():
            log.debug(f"Prompt variable '{m}' not found in prompt template, removed")
            del prompt_variables[m]
        if m in tmp_prompt.input_variables:
            prompt_template = \
                prompt_template.replace("{" + m + "}", "")
            log.debug(f"Placeholder '{m}' not found in prompt variables, removed")
            
    return prompt_variables, prompt_template


def get_caller_info(skip=2, return_short=True, return_string=True):
    """Get the name of a caller in the format module.class.method.

    Adapted from: https://gist.github.com/techtonik/2151727

    Parameters
    ----------
    skip :  int
        Specifies how many levels of stack to skip while getting caller name.
    return_string : bool
        If True, returns the caller info as a string, otherwise as a tuple.

    Returns
    -------
    package : str
        Caller package.
    module : str
        Caller module.
    klass : str
        Caller classname if one otherwise None.
    caller : str
        Caller function or method (if a class exist).
    line : int
        The line of the call.


    Notes
    -----
    skip=1 means "who calls me",
    skip=2 "who calls my caller" etc.

    None is returned if skipped levels exceed stack height.
    """

    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start + 1:
        return None
    
    parentframe = stack[start][0]

    # module and packagename.
    module_info = inspect.getmodule(parentframe)
    if module_info:
        mod = module_info.__name__.split(".")
        package = mod[0]
        module = ".".join(mod[1:])

    # class name.
    klass = ""
    if "self" in parentframe.f_locals:
        klass = parentframe.f_locals["self"].__class__.__name__

    # method or function name.
    caller = None
    if parentframe.f_code.co_name != "<module>":  # top level usually
        caller = parentframe.f_code.co_name

    # call line.
    line = parentframe.f_lineno

    # Remove reference to frame
    # See: https://docs.python.org/3/library/inspect.html#the-interpreter-stack
    del parentframe

    if return_string:
        if return_short:
            return f"{klass}.{caller}"
        else:
            return f"{package}.{module}.{klass}.{caller}::{line}"
    return package, module, klass, caller, line


def langchain_log_prompt(langchain_prompt, title):
    if(get_env("CCAT_DEBUG") == "true"):
        print("\n")
        print(get_colored_text(f"===== {title} =====", "green"))
        for m in langchain_prompt.messages:
            print(get_colored_text(type(m).__name__, "green"))
            if isinstance(m.content, list):
                for sub_m in m.content:
                    if sub_m.get("type") == "text":
                        print(sub_m["text"])
                    elif sub_m.get("type") == "image_url":
                        print("(image)")
                    else:
                        print(" -- Could not log content:", sub_m.keys())
            else:
                print(m.content)
        print(get_colored_text("========================================", "green"))
    return langchain_prompt


def langchain_log_output(langchain_output, title):
    if(get_env("CCAT_DEBUG") == "true"):
        print("\n")
        print(get_colored_text(f"===== {title} =====", "blue"))
        if hasattr(langchain_output, 'content'):
            print(langchain_output.content)
        else:
            print(langchain_output)
        print(get_colored_text("========================================", "blue"))
    return langchain_output


# This is our masterwork during tea time
class singleton:
    instances = {}

    def __new__(cls, class_):
        def getinstance(*args, **kwargs):
            if class_ not in cls.instances:
                cls.instances[class_] = class_(*args, **kwargs)
            return cls.instances[class_]

        return getinstance


# Class mixing pydantic BaseModel with dictionaries (added for backward compatibility, to be deprecated in v2)
class BaseModelDict(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        protected_namespaces=() # avoid warning for `model_xxx` attributes
    )

    def __getitem__(self, key):
        # deprecate dictionary usage
        deprecation_warning(
            f'To get `{key}` use dot notation instead of dictionary keys, example:' 
            f'`obj.{key}` instead of `obj["{key}"]`'
        )

        # return attribute
        return getattr(self, key)

    def __setitem__(self, key, value):
        # deprecate dictionary usage
        deprecation_warning(
            f'To set `{key}` use dot notation instead of dictionary keys, example:'
            f'`obj.{key} = x` instead of `obj["{key}"] = x`'
        )

        # set attribute
        setattr(self, key, value)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __delitem__(self, key):
        delattr(self, key)

    def _get_all_attributes(self):
        # return {**self.model_fields, **self.__pydantic_extra__}
        return self.model_dump()

    def keys(self):
        return self._get_all_attributes().keys()

    def values(self):
        return self._get_all_attributes().values()

    def items(self):
        return self._get_all_attributes().items()

    def __contains__(self, key):
        return key in self.keys()


