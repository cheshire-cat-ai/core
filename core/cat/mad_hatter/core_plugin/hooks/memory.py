from langchain.docstore.document import Document

from cat.mad_hatter.decorators import hook


# Hook called before inserting the first point in memory collection.
# This happens at first lunch and whenever `long_term_memory` is deleted.
# first_point is `langchain.Document` instance
@hook(priority=0)
def before_collection_created(first_point: Document, cat):
    """Hook the first point inserted in memory.

    Allows to edit the first point that is inserted in both *declarative*
    and *episodic* memories when the collections are created. Collection creation
    happens the first time the Cat starts up or after a memory swap through the endpoints.

    Args:
        first_point: `langchain.Document` to be added to the vector memory collection. The `Document`
        has two mandatory properties: `page_content` and `metadata`. The former
        is the string content to be inserted into memory; the latter is a dictionary to store custom metadata.
        cat: Cheshire Car instance to exploit its methods.

    Returns:
        Custom `langchain.Document`. Default
        to:

        first_memory = Document(page_content="I am the Cheshire Cat",
        metadata={
        "source": "cheshire-cat",
        "when": time.time()})
    """
    return first_point
