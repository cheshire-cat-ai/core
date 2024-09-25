from typing import Dict, List
from pydantic import BaseModel
from fastapi import Query, Request, APIRouter, HTTPException, Depends
from qdrant_client import QdrantClient
import time


from cat.looking_glass.cheshire_cat import CheshireCat
from cat.auth.connection import HTTPAuth
from cat.auth.permissions import AuthPermission, AuthResource
from cat.memory.vector_memory import VectorMemory
from cat.looking_glass.stray_cat import StrayCat


class MemoryPointBase(BaseModel):
    content: str
    metadata: Dict = {}


# TODOV2: annotate all endpoints and align internal usage (no qdrant PointStruct, no langchain Document)
class MemoryPoint(MemoryPointBase):
    id: str
    vector: List[float]


router = APIRouter()


# GET memories from recall
@router.get("/recall")
async def recall_memories_from_text(
    request: Request,
    text: str = Query(description="Find memories similar to this text."),
    k: int = Query(default=100, description="How many memories to return."),
    stray=Depends(HTTPAuth(AuthResource.MEMORY, AuthPermission.READ)),
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
            user_filter = {"source": user_id}
        else:
            user_filter = None

        memories = vector_memory.collections[c].recall_memories_from_embedding(
            query_embedding, k=k, metadata=user_filter
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
            "embedder": str(
                ccat.embedder.__class__.__name__
            ),  # TODO: should be the config class name
            "collections": recalled,
        },
    }


# GET collection list with some metadata
@router.get("/collections")
async def get_collections(
    request: Request, stray: StrayCat=Depends(HTTPAuth(AuthResource.MEMORY, AuthPermission.READ))
) -> Dict:
    """Get list of available collections"""
    
    vector_memory: VectorMemory = stray.memory.vectors
    collections = list(vector_memory.collections.keys())
    qdrant_client: QdrantClient = vector_memory.vector_db
    
    collections_metadata = []

    for c in collections:
        coll_meta = qdrant_client.get_collection(c)
        collections_metadata += [{"name": c, "vectors_count": coll_meta.points_count}]

    return {"collections": collections_metadata}


# DELETE all collections
@router.delete("/collections")
async def wipe_collections(
    request: Request,
    stray=Depends(HTTPAuth(AuthResource.MEMORY, AuthPermission.DELETE)),
) -> Dict:
    """Delete and create all collections"""

    vector_memory: VectorMemory = stray.memory.vectors
    collections = list(vector_memory.collections.keys())
    qdrant_client: QdrantClient = vector_memory.vector_db

    to_return = {}
    for c in collections:
        ret = qdrant_client.delete_collection(collection_name=c)
        to_return[c] = ret
    
    ccat: CheshireCat = request.app.state.ccat
    ccat.load_memory()  # recreate the long term memories
    ccat.mad_hatter.find_plugins()

    return {
        "deleted": to_return,
    }


# DELETE one collection
@router.delete("/collections/{collection_id}")
async def wipe_single_collection(
    request: Request,
    collection_id: str,
    stray=Depends(HTTPAuth(AuthResource.MEMORY, AuthPermission.DELETE)),
) -> Dict:
    """Delete and recreate a collection"""

    vector_memory: VectorMemory = stray.memory.vectors
    collections = list(vector_memory.collections.keys())
    qdrant_client: QdrantClient = vector_memory.vector_db
    
    if collection_id not in collections:
        raise HTTPException(
            status_code=400, detail={"error": "Collection does not exist."}
        )

    to_return = {}

    ret = qdrant_client.delete_collection(collection_name=collection_id)
    to_return[collection_id] = ret

    ccat: CheshireCat = request.app.state.ccat
    ccat.load_memory()  # recreate the long term memories
    ccat.mad_hatter.find_plugins()

    return {
        "deleted": to_return,
    }


# CREATE a point in memory
@router.post("/collections/{collection_id}/points", response_model=MemoryPoint)
async def create_memory_point(
    request: Request,
    collection_id: str,
    point: MemoryPointBase,
    stray=Depends(HTTPAuth(AuthResource.MEMORY, AuthPermission.WRITE)),
) -> MemoryPoint:
    """Create a point in memory"""

    # do not touch procedural memory
    if collection_id == "procedural":
        raise HTTPException(
            status_code=400, detail={"error": "Procedural memory is read-only."}
        )

    vector_memory: VectorMemory = stray.memory.vectors
    collections = list(vector_memory.collections.keys())
    if collection_id not in collections:
        raise HTTPException(
            status_code=400, detail={"error": "Collection does not exist."}
        )

    # embed content
    embedding = stray.embedder.embed_query(point.content)

    # ensure source is set
    if not point.metadata.get("source"):
        point.metadata["source"] = (
            stray.user_id
        )  # this will do also for declarative memory

    # ensure when is set
    if not point.metadata.get("when"):
        point.metadata["when"] = time.time() #if when is not in the metadata set the current time

    # create point
    qdrant_point = vector_memory.collections[collection_id].add_point(
        content=point.content, vector=embedding, metadata=point.metadata
    )

    return MemoryPoint(
        metadata=qdrant_point.payload["metadata"],
        content=qdrant_point.payload["page_content"],
        vector=qdrant_point.vector,
        id=qdrant_point.id,
    )


# DELETE memories
@router.delete("/collections/{collection_id}/points/{point_id}")
async def delete_memory_point(
    request: Request,
    collection_id: str,
    point_id: str,
    stray=Depends(HTTPAuth(AuthResource.MEMORY, AuthPermission.DELETE)),
) -> Dict:
    """Delete a specific point in memory"""

    vector_memory: VectorMemory = stray.memory.vectors
    collections = list(vector_memory.collections.keys())

    # check if collection exists
    collections = list(vector_memory.collections.keys())
    if collection_id not in collections:
        raise HTTPException(
            status_code=400, detail={"error": "Collection does not exist."}
        )

    # check if point exists
    points = vector_memory.vector_db.retrieve(
        collection_name=collection_id,
        ids=[point_id],
    )
    if points == []:
        raise HTTPException(status_code=400, detail={"error": "Point does not exist."})

    # delete point
    vector_memory.collections[collection_id].delete_points([point_id])

    return {"deleted": point_id}


@router.delete("/collections/{collection_id}/points")
async def delete_memory_points_by_metadata(
    request: Request,
    collection_id: str,
    metadata: Dict = {},
    stray=Depends(HTTPAuth(AuthResource.MEMORY, AuthPermission.DELETE)),
) -> Dict:
    """Delete points in memory by filter"""

    vector_memory: VectorMemory = stray.memory.vectors
    
    # delete points
    vector_memory.collections[collection_id].delete_points_by_metadata_filter(metadata)

    return {
        "deleted": []  # TODO: Qdrant does not return deleted points?
    }


# DELETE conversation history from working memory
@router.delete("/conversation_history")
async def wipe_conversation_history(
    request: Request,
    stray=Depends(HTTPAuth(AuthResource.MEMORY, AuthPermission.DELETE)),
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
    stray=Depends(HTTPAuth(AuthResource.MEMORY, AuthPermission.READ)),
) -> Dict:
    """Get the specified user's conversation history from working memory"""

    return {"history": stray.working_memory.history}

# GET all the points from a single collection
@router.get("/collections/{collection_id}/points")
async def get_collections_points(
    request: Request,
    collection_id: str,
    limit:int=Query(
        default=100,
        description="How many points to return"
    ),
    offset:str = Query(
        default=None,
        description="If provided (or not empty string) - skip points with ids less than given `offset`"
    ),
    stray=Depends(HTTPAuth(AuthResource.MEMORY, AuthPermission.READ)),
) -> Dict:
    """Retrieve all the points from a single collection

    
    Example
    ----------
    ```
    collection = "declarative"
    res = requests.get(
        f"http://localhost:1865/memory/collections/{collection}/points",
    )
    json = res.json()
    points = json["points"]

    for point in points:
        payload = point["payload"]
        vector = point["vector"]
        print(payload)
        print(vector)
    ```

    Example using offset
    ----------
    ```
    # get all the points with limit 10
    limit = 10
    next_offset = ""
    collection = "declarative"

    while True:
        res = requests.get(
            f"http://localhost:1865/memory/collections/{collection}/points?limit={limit}&offset={next_offset}",
        )
        json = res.json()
        points = json["points"]
        next_offset = json["next_offset"]

        for point in points:
            payload = point["payload"]
            vector = point["vector"]
            print(payload)
            print(vector)
        
        if next_offset is None:
            break
    ```
    """

    # do not allow procedural memory reads via network
    if collection_id == "procedural":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Procedural memory is not readable via API"
            }
        )

    # check if collection exists
    collections = list(stray.memory.vectors.collections.keys())
    if collection_id not in collections:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Collection does not exist."
            }
        )
    
    # if offset is empty string set to null
    if offset == "":
        offset = None
    
    memory_collection = stray.memory.vectors.collections[collection_id]
    points, next_offset = memory_collection.get_all_points(limit=limit, offset=offset)
    
    return {
        "points": points,
        "next_offset": next_offset
    }

