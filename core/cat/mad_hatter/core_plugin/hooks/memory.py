"""Hooks to modify the Cat's memory collections.

Here is a collection of methods to hook the insertion of memories in the vector databases.

"""

from langchain.docstore.document import Document
from cat.memory.vector_memory import VectorMemoryCollection
from cat.mad_hatter.decorators import hook


# Hook called before a memory collection has been created.
# This happens at first launch and whenever the collection is deleted and recreated.
@hook(priority=0)
def before_collection_created(vector_memory_collection: VectorMemoryCollection, cat):
    """Do something before a new collection is created in vectorDB

    Args:
        vector_memory_collection: instance of VectorMemoryCollection wrapping the actual db collection.
        cat: Cheshire Car instance.

    Returns:
        None
    """
    pass


# Hook called after a memory collection has been created.
# This happens at first launch and whenever the collection is deleted and recreated.
@hook(priority=0)
def after_collection_created(vector_memory_collection: VectorMemoryCollection, cat):
    """Do something after a new collection is created in vectorDB

    Args:
        vector_memory_collection: instance of VectorMemoryCollection wrapping the actual db collection.
        cat: Cheshire Car instance.

    Returns:
        None
    """
    pass