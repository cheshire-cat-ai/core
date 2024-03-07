"""The log engine."""

import logging
import sys
import os
import inspect
import traceback
import json
from itertools import takewhile
from pprint import pformat
from loguru import logger


def get_log_level():
    """Return the global LOG level."""
    return os.getenv("LOG_LEVEL", "INFO")


class CatLogEngine:
    """The log engine.

    Engine to filter the logs in the terminal according to the level of severity.

    Attributes
    ----------
    LOG_LEVEL : str
        Level of logging set in the `.env` file.

    Notes
    -----
    The logging level set in the `.env` file will print all the logs from that level to above.
    Available levels are:

        - `DEBUG`
        - `INFO`
        - `WARNING`
        - `ERROR`
        - `CRITICAL`

    Default to `INFO`.

    """

    def __init__(self):
        self.LOG_LEVEL = get_log_level()
        self.default_log()

        # workaround for pdfminer logging
        # https://github.com/pdfminer/pdfminer.six/issues/347
        logging.getLogger("pdfminer").setLevel(logging.WARNING)

    def show_log_level(self, record):
        """Allows to show stuff in the log based on the global setting.

        Parameters
        ----------
        record : dict

        Returns
        -------
        bool

        """
        return record["level"].no >= logger.level(self.LOG_LEVEL).no

    def default_log(self):
        """Set the same debug level to all the project dependencies.

        Returns
        -------
        """

        time = "<green>[{time:YYYY-MM-DD HH:mm:ss.SSS}]</green>"
        level = "<level>{level: <6}</level>"
        origin = "<level>{extra[original_name]}.{extra[original_class]}.{extra[original_caller]}::{extra[original_line]}</level>"
        message = "<level>{message}</level>"
        log_format = f"{time} {level} {origin} \n{message}"

        logger.remove()
        if self.LOG_LEVEL == "DEBUG":
            return logger.add(
                sys.stdout,
                colorize=True,
                format=log_format,
                backtrace=True,
                diagnose=True,
                filter=self.show_log_level
            )
        else:
            return logger.add(
                sys.stdout,
                colorize=True,
                format=log_format,
                filter=self.show_log_level,
                level=self.LOG_LEVEL
            )

    def get_caller_info(self, skip=3):
        """Get the name of a caller in the format module.class.method.

        Copied from: https://gist.github.com/techtonik/2151727

        Parameters
        ----------
        skip :  int
            Specifies how many levels of stack to skip while getting caller name.

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

        An empty string is returned if skipped levels exceed stack height.
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

        return package, module, klass, caller, line

    def __call__(self, msg, level="DEBUG"):
        """Alias of self.log()"""
        self.log(msg, level)

    def debug(self, msg):
        """Logs a DEBUG message"""
        self.log(msg, level="DEBUG")

    def info(self, msg):
        """Logs an INFO message"""
        self.log(msg, level="INFO")

    def warning(self, msg):
        """Logs a WARNING message"""
        self.log(msg, level="WARNING")

    def error(self, msg):
        """Logs an ERROR message"""
        self.log(msg, level="ERROR")

    def critical(self, msg):
        """Logs a CRITICAL message"""
        self.log(msg, level="CRITICAL")

    def log(self, msg, level="DEBUG"):
        """Log a message

        Parameters
        ----------
        msg :
            Message to be logged.
        level : str
            Logging level."""

        (package, module, klass, caller, line) = self.get_caller_info()

        custom_logger = logger.bind(
            original_name=f"{package}.{module}",
            original_line=line,
            original_class=klass,
            original_caller=caller,
        )

        # prettify
        if type(msg) in [dict, list, str]: # TODO: should be recursive
            try:
                msg = json.dumps(msg, indent=4)
            except:
                pass
        else:
            msg = pformat(msg)

        # actual log
        custom_logger.log(level, msg)

    def welcome(self):
        """Welcome message in the terminal."""
        secure = os.getenv('CORE_USE_SECURE_PROTOCOLS', '')
        if secure != '':
            secure = 's'

        cat_host = os.getenv("CORE_HOST", "localhost")
        cat_port = os.getenv("CORE_PORT", "1865")
        cat_address = f'http{secure}://{cat_host}:{cat_port}'

        with open("cat/welcome.txt", 'r') as f:
            print(f.read())

        print('\n=============== ^._.^ ===============\n')
        print(f'Cat REST API:   {cat_address}/docs')
        print(f'Cat PUBLIC:     {cat_address}/public')
        print(f'Cat ADMIN:      {cat_address}/admin\n')
        print('======================================')

# logger instance
log = CatLogEngine()
