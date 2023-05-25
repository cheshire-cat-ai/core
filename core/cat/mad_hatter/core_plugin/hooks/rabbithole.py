"""Hooks to modify the RabbitHole's documents ingestion.

Here is a collection of methods to hook into the RabbitHole execution pipeline.

These hooks allow to intercept the uploaded documents at different places before they are saved into memory.

"""

from typing import List

from cat.utils import log
from langchain.text_splitter import RecursiveCharacterTextSplitter
from cat.mad_hatter.decorators import hook
from langchain.docstore.document import Document


# Hook called just before of inserting a document in vector memory
@hook(priority=0)
def before_rabbithole_insert_memory(doc: Document, cat) -> Document:
    """Hook the `Document` before is inserted in the vector memory.

    Allows to edit and enhance a single `Document` before the *RabbitHole* add it to the declarative vector memory.

    The `Document` has two properties::

        `page_content`: the string with the text to save in memory;
        `metadata`: a dictionary with at least two keys:
            `source`: where the text comes from;
            `when`: timestamp to track when it's been uploaded.

    Args:
        doc: langchain `Document` to be inserted in memory.
        cat: Cheshire Cat instance.

    Returns:
        langchain `Document` that is added in the declarative vector memory.

    """
    return doc


# Hook called just before rabbithole splits text. Input is whole Document
@hook(priority=0)
def before_rabbithole_splits_text(doc: Document, cat) -> Document:
    """Hook the `Document` before is split.

    Allows to edit the whole uploaded `Document` before the *RabbitHole* recursively splits it in shorter ones.

    For instance, the hook allows to change the text or edit/add metadata.

    Args:
        doc: langchain `Document` uploaded in the *RabbitHole* to be ingested.
        cat: Cheshire Cat instance.

    Returns:
        Edited langchain `Document`.

    """
    return doc


# Hook called when rabbithole splits text. Input is whole Document
@hook(priority=0)
def rabbithole_splits_text(
    text: List[Document], chunk_size: int, chunk_overlap: int, cat
) -> List[Document]:
    """Hook into the recursive split pipeline.

    Allows to edit the recursive split the *RabbitHole* applies to chunk the ingested documents.

    This is applied when ingesting a documents and urls from a script, using an endpoint or from the GUI.

    Args:
        text: list of langchain `Document` to chunk.
        chunk_size: length of every chunk in characters.
        chunk_overlap: amount of overlap between consecutive chunks.
        cat: Cheshire Cat instance.

    Returns:
        list of chunked langchain `Document` to be optionally summarized and stored in episodic memory.

    """
    # text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\\n\\n", "\n\n", ".\\n", ".\n", "\\n", "\n", " ", ""],
    )

    # split text
    docs = text_splitter.split_documents(text)

    # remove short texts (page numbers, isolated words, etc.)
    docs = list(filter(lambda d: len(d.page_content) > 10, docs))

    # add metadata, these docs are not summaries
    for doc in docs:
        doc.metadata["is_summary"] = False

    return docs


# Hook called after rabbithole have splitted text into chunks.
#   Input is the chunks
@hook(priority=0)
def after_rabbithole_splitted_text(
    chunks: List[Document], cat
) -> List[Document]:
    """Hook the `Document` after is split.

    Allows to edit the list of `Document` right after the *RabbitHole* chunked them in smaller ones.

    Args:
        chunks: list of langchain `Document`.
        cat: Cheshire Cat instance.

    Returns:
        list of modified chunked langchain `Document` to be optionally summarized and stored in episodic memory.

    """
    return chunks


# Hook called when a list of Document is summarized from the rabbit hole.
# Should return a list of summaries (each is a langchain Document)
# To deactivate summaries, override this hook and just return an empty list
@hook(priority=0)
def rabbithole_summarizes_documents(docs: List[Document], cat) -> List[Document]:
    """Hook into the summarization pipeline.

    Allows to modify how the list of `Document` is summarized before being inserted in the vector memory.

    For example, the hook allows to make the summarization optional or to apply another summarization technique.

    Args:
        docs: list of langchain `Document` to be summarized.
        cat: Cheshire Cat instance.

    Returns:
        list of langchain`Document` with text summaries of the original ones.

    """
    # service variable to store intermediate results
    intermediate_summaries = docs

    # we will store iterative summaries all together in a list
    all_summaries: List[Document] = []

    # loop until there are no groups to summarize
    group_size = 5
    root_summary_flag = False
    separator = "\n --> "
    while not root_summary_flag:
        # make summaries of groups of docs
        new_summaries = []
        for i in range(0, len(intermediate_summaries), group_size):
            group = intermediate_summaries[i: i + group_size]
            group = list(map(lambda d: d.page_content, group))

            text_to_summarize = separator + separator.join(group)
            summary = cat.summarization_chain.run(text_to_summarize)
            summary = Document(page_content=summary)
            summary.metadata["is_summary"] = True
            new_summaries.append(summary)

        # update list of all summaries
        all_summaries = new_summaries.copy() + all_summaries
        intermediate_summaries = new_summaries

        # did we reach root summary?
        root_summary_flag = len(intermediate_summaries) == 1

        log(
            f"Building summaries over {len(intermediate_summaries)} chunks. "
            "Please wait."
        )

    log(all_summaries)

    # return root summary (first element) and all intermediate summaries
    return all_summaries
