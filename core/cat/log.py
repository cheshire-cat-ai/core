"""The log engine."""

import logging
import sys
import os
import inspect
import traceback
from itertools import takewhile
from pprint import pformat
from loguru import logger


def get_log_level():
    """Return the global LOG level."""
    return os.getenv("LOG_LEVEL", "DEBUG")


class CatLogEnine:
    """The log engine."""

    def __init__(self):
        """Initialize log for Cheshire Cat and the dependencies."""
        self.LOG_LEVEL = get_log_level()
        self.default_log()

        # workaround for pdfminer logging
        # https://github.com/pdfminer/pdfminer.six/issues/347
        logging.getLogger("pdfminer").setLevel(logging.WARNING)

    def show_log_level(self, record):
        """Allows to show stuff in the log based on the global setting."""
        return record["level"].no >= logger.level(self.LOG_LEVEL).no

    def default_log(self):
        """Set the same debug level to all the project dependecies."""
        log_format = "<green>[{time:YYYY-MM-DD HH:mm:ss.SSS}]</green> <level>{level: <6}</level> <cyan>{name}.py</cyan> <cyan>{line}</cyan> => <level>{message}</level>"
        logger.remove()
        if self.LOG_LEVEL == "DEBUG":
            return logger.add(
                sys.stdout, colorize=True, format=log_format, backtrace=True, diagnose=True, filter=self.show_log_level
            )
        else:
            return logger.add(sys.stdout, colorize=True, format=log_format, filter=self.show_log_level)

    def get_caller_info(self, skip=3):
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

    def log(self, msg, level="DEBUG"):
        """Add to log based on settings."""
        global logger
        logger.remove()

        # Add real caller for the log
        (package, module, klass, caller, line) = self.get_caller_info()
        context = {
            "original_name": f"{package}.{module}",
            "original_line": line,
            "original_class": klass,
            "original_caller": caller,
        }

        log_format = "<green>[{time:YYYY-MM-DD HH:mm:ss.SSS}]</green> <level>{level: <6}</level> <cyan>{extra[original_name]}.py</cyan> <cyan>{extra[original_line]} ({extra[original_class]}.{extra[original_caller]})</cyan> => <level>{message}</level>"

        _logger = logger

        msg_body = pformat(msg)
        lines = msg_body.splitlines()

        # On debug level print the traceback better
        if self.LOG_LEVEL == "DEBUG":
            if type(msg) is str and not msg.startswith("> "):
                traceback_log_format = "<yellow>{extra[traceback]}</yellow>"
                stack = ""
                _logger.add(
                    sys.stdout,
                    colorize=True,
                    format=traceback_log_format,
                    backtrace=True,
                    diagnose=True,
                    filter=self.show_log_level,
                )
                frames = takewhile(lambda f: "/loguru/" not in f.filename, traceback.extract_stack())
                for f in frames:
                    if f.filename.startswith("/app/./cat"):
                        filename = f.filename.replace("/app/./cat", "")
                        if not filename.startswith("/log.py"):
                            stack = "> " + "".join("{}:{}:{}".format(filename, f.name, f.lineno))
                            context["traceback"] = stack

                            _logger.bind(**context).log(level, "")
                logger.remove()

        _logger.add(
            sys.stdout, colorize=True, format=log_format, backtrace=True, diagnose=True, filter=self.show_log_level
        )

        for line in lines:
            line = line.strip().replace("\\n", "")
            if line != "":
                _logger.bind(**context).log(level, f"{line}")
        # After our custom log we need to set again the logger as default for the other dependencies
        self.default_log()


logEngine = CatLogEnine()


def log(msg, level="DEBUG"):
    """Create function wrapper to class."""
    global logEngine
    return logEngine.log(msg, level)
