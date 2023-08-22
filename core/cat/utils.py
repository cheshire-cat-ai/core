"""Various utiles used from the projects."""

from abc import ABC
from typing import Iterator
from datetime import timedelta

from unstructured.partition.auto import partition
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseBlobParser
from langchain.document_loaders.blob_loaders.schema import Blob


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


class DocxParser(BaseBlobParser, ABC):
    """Custom parser for `.docx` and `.doc` files."""
    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        """This method overrides the `BaseBlobParser` to lazy parse Microsoft `.docx` and `.doc` files.

        Parameters
        ----------
        blob: Blob
            Raw data the `RabbitHole` receives when a file is ingested.

        Returns
        -------
        Iterator[Document]
            Iterator with the parsed text converted to Langchain documents.

        """

        # Load raw data as a file-like object with binary content
        with blob.as_bytes_io() as file:
            # Get the file elements using Unstructured
            elements = partition(file=file)

        # Retrieve the text from each element and format it in a text
        elements = [e.text for e in elements]
        text = "\n".join(elements)

        yield Document(page_content=text, metadata={})
