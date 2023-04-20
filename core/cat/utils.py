from datetime import timedelta
import inspect
import logging
from pprint import pformat

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


def get_caller_info(skip=2):
    """Get the name of a caller in the format module.class.method.
    Copied from: https://gist.github.com/techtonik/2151727
    :arguments:
        - skip (integer): Specifies how many levels of stack
                          to skip while getting caller name.
                          skip=1 means "who calls me",
                          skip=2 "who calls my caller" etc.
    :returns:
        - package (string): caller package.
        - module (string): caller module.
        - klass (string): caller classname if one otherwise None.
        - caller (string): caller function or method (if a class exist).
        - line (int): the line of the call.
        - An empty string is returned if skipped levels exceed stack height.
    """
    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start + 1:
        return ""
    parentframe = stack[start][0]

    # module and packagename.
    module_info = inspect.getmodule(parentframe)
    if module_info:
        mod = module_info.__name__.split(".")
        package = mod[0]
        module = mod[1]

    # class name.
    klass = None
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

    return package, module, klass, caller, line


def log(msg):
    (package, module, klass, caller, line) = get_caller_info()
    color_code = "38;5;219"

    msg_header = "----------------  ^._.^  ----------------"
    msg_body = pformat(msg)
    msg_footer = "-----------------------------------------"

    logging.debug(
        f"\u001b[{color_code}m\033[0.1m{msg_header}\u001b[0m => {package}.{module}.py ({klass}.{caller}(...)) @ {line} line"
    )
    for line in msg_body.splitlines():
        logging.debug(f"\u001b[{color_code}m\033[0.1m{line}")
    logging.debug(f"\u001b[{color_code}m\033[0.1m{msg_footer}")


# Takes in a string of words separated by either hyphens or underscores and returns a string of words in camel case
def to_camel_case(text):
    s = text.replace("-", " ").replace("_", " ").capitalize()
    s = s.split()
    if len(text) == 0:
        return text
    return s[0] + "".join(i.capitalize() for i in s[1:])



def verbal_timedelta(td):
    if td.days != 0:
        abs_days = abs(td.days)
        if abs_days > 7:
            abs_delta = '{} weeks'.format(td.days // 7)
        else:
            abs_delta = '{} days'.format(td.days)
    else:
        abs_minutes = abs(td.seconds) // 60
        if abs_minutes > 60:
            abs_delta = '{} hours'.format(abs_minutes // 60)
        else:
            abs_delta = '{} minutes'.format(abs_minutes)
    if td < timedelta(0):
        return '{} ago'.format(abs_delta)
    else:
        return '{} ago'.format(abs_delta)

