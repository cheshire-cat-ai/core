"""Hooks to modify the RabbitHole's documents ingestion.

Here is a collection of methods to hook into the RabbitHole execution pipeline.

These hooks allow to intercept the uploaded documents at different places before they are saved into memory.

"""

from typing import List
from langchain.text_splitter import TextSplitter
from langchain.docstore.document import Document
from qdrant_client.http.models import PointStruct

from cat.mad_hatter.decorators import hook


@hook(priority=0)
def rabbithole_instantiates_parsers(file_handlers: dict, cat) -> dict:
    """Hook the available parsers for ingesting files in the declarative memory.

    Allows replacing or extending existing supported mime types and related parsers to customize the file ingestion.

    Parameters
    ----------
    file_handlers : dict
        Keys are the supported mime types and values are the related parsers.
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    file_handlers : dict
        Edited dictionary of supported mime types and related parsers.
    """
    return file_handlers


@hook(priority=0)
def rabbithole_instantiates_splitter(text_splitter: TextSplitter, cat) -> TextSplitter:
    """Hook the splitter used to split text in chunks.

    Allows replacing the default text splitter to customize the splitting process.

    Parameters
    ----------
    text_splitter : TextSplitter
        The text splitter used by default.
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    text_splitter : TextSplitter
        An instance of a TextSplitter subclass.
    """

    # example on how to change chunking
    # text_splitter._chunk_size = 64
    # text_splitter._chunk_overlap = 8

    return text_splitter


# Hook called just before of inserting a document in vector memory
@hook(priority=0)
def before_rabbithole_insert_memory(doc: Document, cat) -> Document:
    """Hook the `Document` before is inserted in the vector memory.

    Allows editing and enhancing a single `Document` before the *RabbitHole* add it to the declarative vector memory.

    Parameters
    ----------
    doc : Document
        Langchain `Document` to be inserted in memory.
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    doc : Document
        Langchain `Document` that is added in the declarative vector memory.

    Notes
    -----
    The `Document` has two properties::

        `page_content`: the string with the text to save in memory;
        `metadata`: a dictionary with at least two keys:
            `source`: where the text comes from;
            `when`: timestamp to track when it's been uploaded.

    """
    return doc


# Hook called just before rabbithole splits text. Input is whole Document
@hook(priority=0)
def before_rabbithole_splits_text(docs: List[Document], cat) -> List[Document]:
    """Hook the `Documents` before they are split into chunks.

    Allows editing the uploaded document main Document(s) before the *RabbitHole* recursively splits it in shorter ones.
    Please note that this is a list because parsers can output one or more Document, that are afterwards splitted.

    For instance, the hook allows to change the text or edit/add metadata.

    Parameters
    ----------
    docs : List[Document]
        Langchain `Document`s resulted after parsing the file uploaded in the *RabbitHole*.
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    docs : List[Document]
        Edited Langchain `Document`s.

    """

    return docs


# Hook called after rabbithole have splitted text into chunks.
#   Input is the chunks
@hook(priority=0)
def after_rabbithole_splitted_text(chunks: List[Document], cat) -> List[Document]:
    """Hook the `Document` after is split.

    Allows editing the list of `Document` right after the *RabbitHole* chunked them in smaller ones.

    Parameters
    ----------
    chunks : List[Document]
        List of Langchain `Document`.
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    chunks : List[Document]
        List of modified chunked langchain documents to be stored in the episodic memory.

    """

    return chunks


# TODO_HOOK: is this useful or just a duplication of `after_rabbithole_splitted_text` ?
# Hook called when a list of Document is going to be inserted in memory from the rabbit hole.
# Here you can edit/summarize the documents before inserting them in memory
# Should return a list of documents (each is a langchain Document)
@hook(priority=0)
def before_rabbithole_stores_documents(docs: List[Document], cat) -> List[Document]:
    """Hook into the memory insertion pipeline.

    Allows modifying how the list of `Document` is inserted in the vector memory.

    For example, this hook is a good point to summarize the incoming documents and save both original and
    summarized contents.
    An official plugin is available to test this procedure.

    Parameters
    ----------
    docs : List[Document]
        List of Langchain `Document` to be edited.
    cat: CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    docs : List[Document]
        List of edited Langchain documents.

    """

    return docs


@hook(priority=0)
def after_rabbithole_stored_documents(
    source, stored_points: List[PointStruct], cat
) -> None:
    """Hook the Document after is inserted in the vector memory.

    Allows editing and enhancing the list of Document after is inserted in the vector memory.

    Parameters
    ----------
    source: str
        Name of ingested file/url
    docs : List[PointStruct]
        List of Qdrant PointStruct just inserted into the db.
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    None
    """
    pass
