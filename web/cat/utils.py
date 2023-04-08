import inspect
import logging


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
    color_code = "38;5;200"

    msg_header = "----------------  ^._.^  ----------------"
    msg_footer = "-----------------------------------------"

    logging.debug(
        f"\n\n\u001b[{color_code}m\033[1;3m{msg_header}\u001b[0m => {package}.{module}.py ({klass}.{caller}(...)) @ {line} line"
    )
    logging.debug(msg)
    logging.debug(f"\n\u001b[{color_code}m\033[1;3m{msg_footer}\u001b[0m\n")
