"""Various utiles used from the projects."""
import os
import inspect
import traceback
from datetime import timedelta
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict

from langchain.evaluation import StringDistance, load_evaluator, EvaluatorType
from langchain_core.output_parsers import JsonOutputParser


from cat.log import log


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
    secure = os.getenv('CORE_USE_SECURE_PROTOCOLS', '')
    if secure != '':
        secure = 's'
    cat_host = os.getenv('CORE_HOST', 'localhost')
    cat_port = os.getenv('CORE_PORT', '1865')
    return f'http{secure}://{cat_host}:{cat_port}/'


def get_base_path():
    """Allows exposing the base path."""
    return 'cat/'


def get_plugins_path():
    """Allows exposing the plugins' path."""
    return os.path.join(get_base_path(), 'plugins/')


def get_static_url():
    """Allows exposing the static server url."""
    return get_base_url() + 'static/'


def get_static_path():
    """Allows exposing the static files' path."""
    return os.path.join(get_base_path(), 'static/')

def is_https(url):
    try:
        parsed_url = urlparse(url)
        return parsed_url.scheme == 'https'
    except Exception as e:
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

        log.error(error_description) # just to make sure the message is read both front and backend

    return error_description


def levenshtein_distance(prediction: str, reference: str) -> int:
    jaro_evaluator = load_evaluator(EvaluatorType.STRING_DISTANCE, distance=StringDistance.LEVENSHTEIN)
    result = jaro_evaluator.evaluate_strings(
        prediction=prediction,
        reference=reference,
    )
    return result['score']


def parse_json(json_string: str, pydantic_model: BaseModel = None) -> dict:

    # instantiate parser
    parser = JsonOutputParser(pydantic_object=pydantic_model)
    
    # clean escapes (small LLM error)
    json_string_clean = json_string.replace("\_", "_").replace("\-", "-")

    # first "{" occurrence (required by parser)
    start_index = json_string_clean.index("{")
    
    # parse
    return parser.parse(json_string_clean[start_index:])


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
        extra='allow',
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    def __getitem__(self, key):

        # deprecate dictionary usage
        stack = traceback.extract_stack(limit=2)
        line_code = traceback.format_list(stack)[0].split('\n')[1].strip()
        log.warning(f"Deprecation Warning: to get '{key}' use dot notation instead of dictionary keys, example: `obj.{key}` instead of `obj['{key}']`")
        log.warning(line_code)

        # return attribute
        return getattr(self, key)

    def __setitem__(self, key, value):
        
        # deprecate dictionary usage
        stack = traceback.extract_stack(limit=2)
        line_code = traceback.format_list(stack)[0].split('\n')[1].strip()
        log.warning(f'Deprecation Warning: to set {key} use dot notation instead of dictionary keys, example: `obj.{key} = x` instead of `obj["{key}"] = x`')
        log.warning(line_code)

        # set attribute
        setattr(self, key, value)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __delitem__(self, key):
        delattr(self, key)

    def _get_all_attributes(self):
        #return {**self.model_fields, **self.__pydantic_extra__}
        return self.model_dump()

    def keys(self):
        return self._get_all_attributes().keys()

    def values(self):
        return self._get_all_attributes().values()

    def items(self):
        return self._get_all_attributes().items()

    def __contains__(self, key):
        return key in self.keys()