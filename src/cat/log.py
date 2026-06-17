import os
import sys
import json
import traceback
from pprint import pformat
from loguru import logger

from cat.env import get_env, get_env_bool

def get_log_level():
    """Return the global LOG level."""
    return get_env("CCAT_LOG_LEVEL")


class LogEngine:
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

    Default to `CCAT_LOG_LEVEL` env variable (`INFO`).
    """

    def __init__(self):
        self.LOG_LEVEL = get_log_level()
        self.default_log()

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
        """Set the same debug level to all the project dependencies."""

        level = "<level>{level}:</level>"
        # time = "<green>[{time:YYYY-MM-DD HH:mm:ss.SSS}]</green>"
        # origin = "<level>{extra[original_name]}.{extra[original_class]}.{extra[original_caller]}::{extra[original_line]}</level>"
        message = "<level>{message}</level>"
        log_format = f"{level}\t{message}"

        logger.remove()
        logger.add(
            sys.stdout,
            level=self.LOG_LEVEL,
            colorize=True,
            format=log_format,
            # backtrace=True,
            # diagnose=True,
            filter=self.show_log_level,
        )

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
        # Only print the traceback if an exception handler is being executed
        self.print_short_traceback()

    def critical(self, msg):
        """Logs a CRITICAL message"""
        self.log(msg, level="CRITICAL")
        self.print_short_traceback()

    def log(self, msg, level="DEBUG"):
        """Log a message

        Parameters
        ----------
        msg :
            Message to be logged.
        level : str
            Logging level."""

        # prettify
        if isinstance(msg, str):
            pass
        elif type(msg) in [dict, list, tuple]:  # TODO: should be recursive
            try:
                msg = json.dumps(msg, indent=4)
            except Exception:
                msg = str(msg)
        else:
            msg = pformat(msg)

        # actual log
        lines = msg.split("\n")
        for line in lines:
            logger.log(level, line)

    def deprecation_warning(self, message: str, skip=3):
        """
        Log a deprecation warning with caller's information.
        "skip" is the number of stack levels to go back to the caller info.
        """

        from cat.utils import get_caller_info
        caller = get_caller_info(skip, return_short=False)

        # Format and log the warning message
        log.warning(
            f"{caller} Deprecation Warning: {message})"
        )

    def print_short_traceback(self):
        if sys.exc_info()[0] is not None:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            formatted_traceback = \
                traceback.format_exception(exc_type, exc_value, exc_traceback)
            if len(formatted_traceback) > 10:
                formatted_traceback = formatted_traceback[-10:]
            for err in formatted_traceback:
                print(self.colored_text(err, "red"))
                
    def welcome(self):
        """Welcome message in the terminal."""
 
        from cat import paths
        cat_address = get_env("CCAT_URL")

        if os.path.exists( paths.DATA_PATH + "/.welcome" ):
            print("\n^._.^\n")
        else:
            print("\n\n")
            with open(paths.BASE_PATH + "/welcome.txt", "r") as f:
                print(f.read())

            left_margin = " " * 15
            print(f"\n\n{left_margin} WEB UI:           {cat_address}")
            print(f"{left_margin} API PLAYGROUND:   {cat_address}/docs\n\n")
            open( paths.DATA_PATH + "/.welcome", "w").close()

        # self.log_examples()

    def colored_text(self, text: str, color: str):
        """Get colored text.

        Args:
            text: The text to color.
            color: The color to use.

        Returns:
            The colored text. Supports blue, yellow, pink, green and red
        """

        colors = {
            "blue": "36;1",
            "yellow": "33;1",
            "pink": "38;5;200",
            "green": "32;1",
            "red": "31;1",
        }

        color_str = colors[color]
        return f"\u001b[{color_str}m{text}\u001b[0m"

    def convo_summary(self, system_prompt, messages, agent_slug):
        """Log a summary of the conversation sent to the LLM."""

        if not get_env_bool("CCAT_DEBUG"):
            return

        c = self.colored_text
        bar = c("━" * 60, "blue")

        lines = ["", bar, c(f"  🐱 {agent_slug}", "blue"), bar]

        # System prompt
        trunc = system_prompt[:60] + "..." if len(system_prompt) > 60 else system_prompt
        lines.append(c("  system  ", "yellow") + trunc.replace("\n", " "))

        # Messages
        for msg in messages:
            content = self._summarize_content(msg)

            if msg.role == "user":
                lines.append(c("  user    ", "green") + content)
            elif msg.role == "assistant":
                if msg.tool_calls:
                    tool_names = ", ".join(tc.name for tc in msg.tool_calls)
                    lines.append(c("  agent   ", "pink") + f"🔧 {tool_names}")
                    if content:
                        lines.append(c("          ", "pink") + content)
                else:
                    lines.append(c("  agent   ", "pink") + f"💬 {content}")
            elif msg.role == "tool":
                lines.append(c("  tool    ", "yellow") + content)

        lines.append(bar + "\n")
        print("\n".join(lines))

    def _summarize_content(self, msg):
        parts = []
        for block in msg.content:
            if hasattr(block, "text"):
                t = block.text.replace("\n", " ").strip()
                parts.append((t[:80] + "...") if len(t) > 80 else t)
            else:
                parts.append(f"[{block.type}]")
        return " ".join(parts)

    def log_examples(self):
        """Log examples for the log engine."""

        for c in [self, "Hello there!", {"ready", "set", "go"}, [1, 4, "sdfsf"], {"a": 1, "b": {"c": 2}}]:
            self.debug(c)
            self.info(c)
            self.warning(c)
            self.error(c)
            self.critical(c)

        def intentional_error():
            print(42/0)

        try:
            intentional_error()
        except Exception:
            self.error("This error is just for demonstration purposes.")

# logger instance
log = LogEngine()
