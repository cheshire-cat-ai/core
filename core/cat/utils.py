"""Various utiles used from the projects."""
import pathlib
import mimetypes
from datetime import timedelta


def to_camel_case(text):
    """Take in a string of words separated by either hyphens or underscores and returns a string of words in camel case."""
    s = text.replace("-", " ").replace("_", " ").capitalize()
    s = s.split()
    if len(text) == 0:
        return text
    return s[0] + "".join(i.capitalize() for i in s[1:])


def verbal_timedelta(td):
    """Convert a timedelta in human form."""
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


def guess_mimetype_from_filename(
    filename: str,
    admitted_types: dict[str, str] | None = None
) -> str | None:
    """
    Guesses any MIME type from the input `filename` extension. The guessing
    process first uses the `mimetypes` module to guess the MIME type.
    If `mimetypes` can't guess the MIME type or guesses it incorrectly, this
    function falls back on a dictionary of admitted types.

    Args:
        filename (str): Input filename.
        admitted_types (dict[str, str] | None, optional): Dictionary mapping
            file extensions to MIME types. If None, a default dictionary is
            used. Defaults to None.

    Returns:
        str | None: The guessed MIME type. If the MIME type can't be guessed
            from the filename, returns None.
    """
    file_extension = pathlib.Path(filename).suffix

    if admitted_types is None:
        admitted_types = {
            ".txt": "text/plain",
            ".bat": "text/plain",
            ".c": "text/plain",
            ".h": "text/plain",
            ".ksh": "text/plain",
            ".pl": "text/plain",
            ".asc": "text/plain",
            ".text": "text/plain",
            ".pot": "text/plain",
            ".brf": "text/plain",
            ".srt": "text/plain",
            ".md": "text/markdown",
            ".markdown": "text/markdown",
            ".pdf": "application/pdf"
        }

    return (
        mimetypes.guess_type(filename)[0]
        or admitted_types.get(file_extension)
    )
