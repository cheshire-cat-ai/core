from typing import Dict
from cat.headers import check_user_id
from cat.routes.types import ResponseMemoryRecall, ResponseCollections, ResponseDelete, ResponseConversationHistory
from fastapi import Query, Request, APIRouter, HTTPException, Depends

router = APIRouter()


# GET memories from recall
@router.get("/recall/")
async def recall_memories_from_text(
    request: Request,
    text: str = Query(description="Find memories similar to this text."),
    k: int = Query(default=100, description="How many memories to return."),
    user_id = Depends(check_user_id)
) -> ResponseMemoryRecall:
    """Search k memories similar to given text."""

    ccat = request.app.state.ccat
    vector_memory = ccat.memory.vectors

    # Embed the query to plot it in the Memory page
    query_embedding = ccat.embedder.embed_query(text)
    query = {
        "text": text,
        "vector": query_embedding,
    }

    # Loop over collections and retrieve nearby memories
    collections = list(vector_memory.collections.keys())
    recalled = {}
    for c in collections:

        # only episodic collection has users
        if c == "episodic":
            user_filter = {
                'source': user_id
            }
        else:
            user_filter = None

        memories = vector_memory.collections[c].recall_memories_from_embedding(
            query_embedding,
            k=k,
            metadata=user_filter
        )

        recalled[c] = []
        for metadata, score, vector, id in memories:
            memory_dict = dict(metadata)
            memory_dict.pop("lc_kwargs", None)  # langchain stuff, not needed
            memory_dict["id"] = id
            memory_dict["score"] = float(score)
            memory_dict["vector"] = vector
            recalled[c].append(memory_dict)

    result = {
        "query": query,
        "vectors": {
            "embedder": str(ccat.embedder.__class__.__name__),  # TODO: should be the config class name
            "collections": recalled
        }
    }

    return ResponseMemoryRecall(**result)


# GET collection list with some metadata
@router.get("/collections/")
async def get_collections(request: Request) -> ResponseCollections:
    """Get list of available collections"""

    ccat = request.app.state.ccat
    vector_memory = ccat.memory.vectors
    collections = list(vector_memory.collections.keys())

    collections_metadata = []

    for c in collections:
        coll_meta = vector_memory.vector_db.get_collection(c)
        collections_metadata += [{
            "name": c,
            "vectors_count": coll_meta.vectors_count
        }]

    result = {
        "collections": collections_metadata
    }

    return ResponseCollections(**result)


# DELETE all collections
@router.delete("/collections/")
async def wipe_collections(request: Request) -> ResponseDelete:
    """Delete and create all collections"""

    ccat = request.app.state.ccat
    collections = list(ccat.memory.vectors.collections.keys())
    vector_memory = ccat.memory.vectors

    to_return = {}
    for c in collections:
        ret = vector_memory.vector_db.delete_collection(collection_name=c)
        to_return[c] = ret

    ccat.load_memory()  # recreate the long term memories
    ccat.mad_hatter.find_plugins()
    ccat.mad_hatter.embed_tools()

    result = {
        "deleted": to_return,
    }

    return ResponseDelete(**result)


# DELETE one collection
@router.delete("/collections/{collection_id}/")
async def wipe_single_collection(request: Request, collection_id: str) -> ResponseDelete:
    """Delete and recreate a collection"""

    ccat = request.app.state.ccat
    vector_memory = ccat.memory.vectors

    # check if collection exists
    collections = list(vector_memory.collections.keys())
    if collection_id not in collections:
        raise HTTPException(
            status_code=400,
            detail={"error": "Collection does not exist."}
        )

    to_return = {}

    ret = vector_memory.vector_db.delete_collection(collection_name=collection_id)
    to_return[collection_id] = ret

    ccat.load_memory()  # recreate the long term memories
    ccat.mad_hatter.find_plugins()
    ccat.mad_hatter.embed_tools()

    result = {
        "deleted": to_return,
    }

    return ResponseDelete(**result)


# DELETE memories
@router.delete("/collections/{collection_id}/points/{memory_id}/")
async def wipe_memory_point(
    request: Request,
    collection_id: str,
    memory_id: str
) -> ResponseDelete:
    """Delete a specific point in memory"""

    ccat = request.app.state.ccat
    vector_memory = ccat.memory.vectors

    # check if collection exists
    collections = list(vector_memory.collections.keys())
    if collection_id not in collections:
        raise HTTPException(
            status_code=400,
            detail={"error": "Collection does not exist."}
        )

    # check if point exists
    points = vector_memory.vector_db.retrieve(
        collection_name=collection_id,
        ids=[memory_id],
    )
    if points == []:
        raise HTTPException(
            status_code=400,
            detail={"error": "Point does not exist."}
        )

    # delete point
    vector_memory.collections[collection_id].delete_points([memory_id])

    result = {
        "deleted": memory_id
    }

    return ResponseDelete(**result)


@router.delete("/collections/{collection_id}/points/")
async def wipe_memory_points_by_metadata(
    request: Request,
    collection_id: str,
    metadata: Dict = {},
) -> ResponseDelete:
    """Delete points in memory by filter"""

    ccat = request.app.state.ccat
    vector_memory = ccat.memory.vectors

    # delete points
    vector_memory.collections[collection_id].delete_points_by_metadata_filter(metadata)

    result = {
        "deleted": True # TODO: Return list of deleted points by Qdrant
    }

    return ResponseDelete(**result)


# DELETE conversation history from working memory
@router.delete("/conversation_history/")
async def wipe_conversation_history(
    request: Request,
    user_id = Depends(check_user_id),
) -> ResponseDelete:
    """Delete the specified user's conversation history from working memory"""

    # TODO: Add possibility to wipe the working memory of specified user id

    ccat = request.app.state.ccat
    ccat.working_memory["history"] = []

    result = {
        "deleted": True,
    }

    return ResponseDelete(**result)


# GET conversation history from working memory
@router.get("/conversation_history/")
async def get_conversation_history(
    request: Request,
    user_id = Depends(check_user_id),
) -> ResponseConversationHistory:
    """Get the specified user's conversation history from working memory"""

    # TODO: Add possibility to get the working memory of specified user id

    ccat = request.app.state.ccat
    history = ccat.working_memory["history"]

    result = {
        "history": history
    }

    return ResponseConversationHistory(**result)