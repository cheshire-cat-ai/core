from typing import List

from cat.utils import log
from cat.mad_hatter.decorators import hook
from langchain.docstore.document import Document


# Hook called just before of inserting documents in vector memory
@hook(priority=0)
def before_rabbithole_insert_memory(doc, cat):
    return doc


# Hook called when a list of Document is summarized.
# Should return a list of summaries (each is a langchain.Document)
# To deactivate summaries, just return an empty list
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
            group = intermediate_summaries[i : i + group_size]
            group = list(map(lambda d: d.page_content, group))

            summary = cat.summarization_chain.run(separator + separator.join(group))
            summary = Document(page_content=summary)
            new_summaries.append(summary)

        # update list of all summaries
        all_summaries = new_summaries.copy() + all_summaries
        intermediate_summaries = new_summaries

        # did we reach root summary?
        root_summary_flag = len(intermediate_summaries) == 1

        log(
            "Building summaries over {len(intermediate_summaries)} chunks. Please wait."
        )

    log(all_summaries)

    # return root summary (first element) and all intermediate summaries
    return all_summaries
