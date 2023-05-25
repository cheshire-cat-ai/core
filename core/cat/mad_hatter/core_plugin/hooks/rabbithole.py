from typing import List

from cat.utils import log
from langchain.text_splitter import RecursiveCharacterTextSplitter
from cat.mad_hatter.decorators import hook
from langchain.docstore.document import Document


# Hook called just before of inserting a document in vector memory
@hook(priority=0)
def before_rabbithole_insert_memory(doc: Document, cat) -> Document:
    return doc


# Hook called just before rabbithole splits text. Input is whole Document
@hook(priority=0)
def before_rabbithole_splits_text(doc: Document, cat) -> Document:
    return doc


# Hook called when rabbithole splits text. Input is whole Document
@hook(priority=0)
def rabbithole_splits_text(
    text, chunk_size: int, chunk_overlap: int, cat
) -> List[Document]:
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
    return chunks


# Hook called when a list of Document is summarized from the rabbit hole.
# Should return a list of summaries (each is a langchain Document)
# To deactivate summaries, override this hook and just return an empty list
@hook(priority=0)
def rabbithole_summarizes_documents(docs, cat) -> List[Document]:
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
