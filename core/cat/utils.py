"""Various utiles used from the projects."""
import os
from datetime import timedelta


def to_camel_case(text :str ) -> str:
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
    """Allows the Cat expose the base url."""
    secure = os.getenv('CORE_USE_SECURE_PROTOCOLS', '')
    if secure != '':
        secure = 's'
    return f'http{secure}://{os.environ["CORE_HOST"]}:{os.environ["CORE_PORT"]}/'

def get_base_path():
    """Allows the Cat expose the base path."""
    return "cat/"

def get_plugin_path():
    """Allows the Cat expose the plugins path."""
    return os.path.join(get_base_path(), "plugins/")

def get_static_url():
    """Allows the Cat expose the static server url."""
    return get_base_url() + "static/"

def get_static_path():
    """Allows the Cat expose the static files path."""
    return os.path.join(get_base_path(), "static/")
