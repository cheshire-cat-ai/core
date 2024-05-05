from typing import Dict
from cat.headers import session
from fastapi import Query, Request, APIRouter, HTTPException, Depends

router = APIRouter()

# GET memories from recall
@router.get("/recall")
async def recall_memories_from_text(
    request: Request,
    text: str = Query(description="Find memories similar to this text."),
    k: int = Query(default=100, description="How many memories to return."),
    stray = Depends(session),
) -> Dict:
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
        user_id = stray.user_id
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

    return {
        "query": query,
        "vectors": {
            "embedder": str(ccat.embedder.__class__.__name__),  # TODO: should be the config class name
            "collections": recalled
        }
    }


# GET collection list with some metadata
@router.get("/collections")
async def get_collections(request: Request) -> Dict:
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

    return {
        "collections": collections_metadata
    }


# DELETE all collections
@router.delete("/collections")
async def wipe_collections(
    request: Request,
) -> Dict:
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

    return {
        "deleted": to_return,
    }


# DELETE one collection
@router.delete("/collections/{collection_id}")
async def wipe_single_collection(request: Request, collection_id: str) -> Dict:
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

    return {
        "deleted": to_return,
    }


# DELETE memories
@router.delete("/collections/{collection_id}/points/{memory_id}")
async def wipe_memory_point(
    request: Request,
    collection_id: str,
    memory_id: str
) -> Dict:
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

    return {
        "deleted": memory_id
    }


@router.delete("/collections/{collection_id}/points")
async def wipe_memory_points_by_metadata(
    request: Request,
    collection_id: str,
    metadata: Dict = {},
) -> Dict:
    """Delete points in memory by filter"""

    ccat = request.app.state.ccat
    vector_memory = ccat.memory.vectors

    # delete points
    vector_memory.collections[collection_id].delete_points_by_metadata_filter(metadata)

    return {
        "deleted": [] # TODO: Qdrant does not return deleted points?
    }


# DELETE conversation history from working memory
@router.delete("/conversation_history")
async def wipe_conversation_history(
    request: Request,
    stray = Depends(session),
) -> Dict:
    """Delete the specified user's conversation history from working memory"""

    stray.working_memory.history = []

    return {
        "deleted": True,
    }


# GET conversation history from working memory
@router.get("/conversation_history")
async def get_conversation_history(
    request: Request,
    stray = Depends(session),
) -> Dict:
    """Get the specified user's conversation history from working memory"""

    return {
        "history": stray.working_memory.history
    }