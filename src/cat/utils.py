"""Various utiles used from the projects."""

import base64
import inspect
import mimetypes
from typing import Any

from cat import log


def levenshtein_distance(a: str, b: str) -> float:
    if not a and not b:
        return 0.0
    if not a or not b:
        return 1.0
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, n + 1):
            temp = dp[j]
            dp[j] = prev if a[i - 1] == b[j - 1] else 1 + min(prev, dp[j], dp[j - 1])
            prev = temp
    return dp[n] / max(m, n)


async def load_image_base64(source: str) -> tuple[str, str]:
    """Load an image from a file path or URL and return (base64_string, mime_type).

    Parameters
    ----------
    source : str
        A local file path or HTTP/HTTPS URL pointing to an image.

    Returns
    -------
    tuple[str, str]
        Base64-encoded image content and its MIME type (e.g. ``image/png``).
    """
    if source.startswith("http://") or source.startswith("https://"):
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(source)
            response.raise_for_status()
            data = response.content
            mime_type = response.headers.get("content-type", "application/octet-stream").split(";")[0].strip()
    else:
        with open(source, "rb") as f:
            data = f.read()
        mime_type, _ = mimetypes.guess_type(source)
        if mime_type is None:
            raise ValueError(f"Cannot determine MIME type for file: {source}")

    return base64.b64encode(data).decode("utf-8"), mime_type


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


async def run_sync_or_async(f, *args, **kwargs) -> Any:
    if inspect.iscoroutinefunction(f):
        return await f(*args, **kwargs)
    path = inspect.getfile(f)
    log.deprecation_warning(f"Function {f.__name__} in {path} should be async.")
    return f(*args, **kwargs)


