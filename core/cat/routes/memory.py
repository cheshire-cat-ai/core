from typing import Dict

from fastapi import Query, Request, APIRouter

router = APIRouter()


# DELETE delete_memories
@router.delete("/point/{memory_id}/")
async def delete_element_in_memory(memory_id: str) -> Dict:
    """Delete specific element in memory."""
    
    return {"error": "to be implemented"}


# GET recall_memories
@router.get("/recall/")
async def recall_memories_from_text(
    request: Request,
    text: str = Query(description="Find memories similar to this text."),
    k: int = Query(default=100, description="How many memories to return."),
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
        memories = vector_memory.collections[c].recall_memories_from_embedding(query_embedding, k=k, threshold=0.0)
        recalled[c] = [dict(m[0]) | {"score": float(m[1])} | {"vector": m[2]} for m in memories]
    
    return {
        "query": query,
        "vectors": {
            "embedder": str(ccat.embedder.__class__.__name__), # TODO: should be the config class name
            "collections": recalled
        }
    }


# GET collection list with some metadata
@router.get("/collections/")
async def get_collections(request: Request) -> Dict:
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
        "status": "success", 
        "results": len(collections_metadata), 
        "collections": collections_metadata
    }


# DELETE one collection
@router.delete("/collections/{collection_id}")
async def wipe_single_collection(request: Request, collection_id: str = "") -> Dict:
    """Delete and recreate a collection"""

    to_return = {}
    if collection_id != "":
        ccat = request.app.state.ccat
        vector_memory = ccat.memory.vectors

        ret = vector_memory.vector_db.delete_collection(collection_name=collection_id)
        to_return[collection_id] = ret

        ccat.bootstrap()  # recreate the long term memories

    return to_return


# DELETE all collections
@router.delete("/wipe-collections/")
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

    ccat.bootstrap()  # recreate the long term memories

    return to_return

#DELETE conversation history from working memory
@router.delete("/working-memory/conversation-history/")
async def wipe_conversation_history(
    request: Request,
) -> Dict:
    """Delete conversation history from working memory"""

    ccat = request.app.state.ccat
    ccat.working_memory["history"] = []

    return {
        "deleted": "true",
    }
