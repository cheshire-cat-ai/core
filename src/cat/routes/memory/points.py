from typing import Dict, List
from pydantic import BaseModel
from fastapi import Query, Body, Request, APIRouter, HTTPException
import time

from cat.auth.permissions import AuthPermission, AuthResource, check_permissions
from cat.memory.vector_memory import VectorMemory
from cat.looking_glass.stray_cat import StrayCat
from cat.log import log

class MemoryPointBase(BaseModel):
    content: str
    metadata: Dict = {}


# TODOV2: annotate all endpoints and align internal usage (no qdrant PointStruct, no langchain Document)
class MemoryPoint(MemoryPointBase):
    id: str
    vector: List[float]


router = APIRouter()


# GET memories from recall
@router.get("/recall", deprecated=True)
async def recall_memory_points_from_text(
    request: Request,
    text: str = Query(description="Find memories similar to this text."),
    k: int = Query(default=100, description="How many memories to return."),
    cat: StrayCat = check_permissions(AuthResource.MEMORY, AuthPermission.READ),
) -> Dict:
    """Search k memories similar to given text."""
    log.warning("Deprecated: This endpoint will be removed in the next major version.")

    # Embed the query to plot it in the Memory page
    query_embedding = cat.embedder.embed_query(text)
    query = {
        "text": text,
        "vector": query_embedding,
    }

    # Loop over collections and retrieve nearby memories
    collections = list(
        cat.memory.vectors.collections.keys()
    )
    recalled = {}
    for c in collections:
        # only episodic collection has users
        user_id = cat.user_id
        if c == "episodic":
            user_filter = {"source": user_id}
        else:
            user_filter = None

        memories = cat.memory.vectors.collections[c].recall_memories_from_embedding(
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
                cat.embedder.__class__.__name__
            ),  # TODO: should be the config class name
            "collections": recalled,
        },
    }

# POST memories from recall
@router.post("/recall")
async def recall_memory_points(
    request: Request,
    text: str = Body(description="Find memories similar to this text."),
    k: int = Body(default=100, description="How many memories to return."),
    metadata: Dict = Body(default={}, 
                        description="Flat dictionary where each key-value pair represents a filter." 
                                    "The memory points returned will match the specified metadata criteria."
                        ),
    cat: StrayCat = check_permissions(AuthResource.MEMORY, AuthPermission.READ),
) -> Dict:
    """Search k memories similar to given text with specified metadata criteria.
        
    Example
    ----------
    ```
    collection = "episodic"
    content = "MIAO!"
    metadata = {"custom_key": "custom_value"}
    req_json = {
        "content": content,
        "metadata": metadata,
    }
    # create a point
    res = requests.post(
        f"http://localhost:1865/memory/collections/{collection}/points", json=req_json
    )

    # recall with metadata
    req_json = {
        "text": "CAT", 
        "metadata":{"custom_key":"custom_value"}
    }
    res = requests.post(
        f"http://localhost:1865/memory/recall", json=req_json
    )
    json = res.json()
    print(json)
    ```

    """

    # Embed the query to plot it in the Memory page
    query_embedding = cat.embedder.embed_query(text)
    query = {
        "text": text,
        "vector": query_embedding,
    }

    # Loop over collections and retrieve nearby memories
    collections = list(
        cat.memory.vectors.collections.keys()
    )
    recalled = {}
    for c in collections:
        # only episodic collection has users
        user_id = cat.user_id
        if c == "episodic":
            metadata["source"] = user_id
        else:
            metadata.pop("source", None)

        memories = cat.memory.vectors.collections[c].recall_memories_from_embedding(
            query_embedding, k=k, metadata=metadata
        )

        recalled[c] = []
        for metadata_memories, score, vector, id in memories:
            memory_dict = dict(metadata_memories)
            memory_dict.pop("lc_kwargs", None)  # langchain stuff, not needed
            memory_dict["id"] = id
            memory_dict["score"] = float(score)
            memory_dict["vector"] = vector
            recalled[c].append(memory_dict)

    return {
        "query": query,
        "vectors": {
            "embedder": str(
                cat.embedder.__class__.__name__
            ),  # TODO: should be the config class name
            "collections": recalled,
        },
    }

# CREATE a point in memory
@router.post("/collections/{collection_id}/points", response_model=MemoryPoint)
async def create_memory_point(
    request: Request,
    collection_id: str,
    point: MemoryPointBase,
    cat: StrayCat = check_permissions(AuthResource.MEMORY, AuthPermission.WRITE),
) -> MemoryPoint:
    """Create a point in memory"""

    # do not touch procedural memory
    if collection_id == "procedural":
        raise HTTPException(
            status_code=400, detail={"error": "Procedural memory is read-only."}
        )

    vector_memory: VectorMemory = cat.memory.vectors
    collections = list(vector_memory.collections.keys())
    if collection_id not in collections:
        raise HTTPException(
            status_code=400, detail={"error": "Collection does not exist."}
        )

    # embed content
    embedding = cat.embedder.embed_query(point.content)

    # ensure source is set
    if not point.metadata.get("source"):
        point.metadata["source"] = (
            cat.user_id
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


@router.delete("/collections/{collection_id}/points/{point_id}")
async def delete_memory_point(
    request: Request,
    collection_id: str,
    point_id: str,
    cat: StrayCat = check_permissions(AuthResource.MEMORY, AuthPermission.DELETE),
) -> Dict:
    """Delete a specific point in memory"""

    vector_memory: VectorMemory = cat.memory.vectors
    collections = list(vector_memory.collections.keys())

    # check if collection exists
    if collection_id not in collections:
        raise HTTPException(
            status_code=400, detail={"error": "Collection does not exist."}
        )

    # check if point exists
    points = vector_memory.collections[collection_id].get_points(
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
    cat: StrayCat = check_permissions(AuthResource.MEMORY, AuthPermission.DELETE),
) -> Dict:
    """Delete points in memory by filter"""

    vector_memory: VectorMemory = cat.memory.vectors
    
    # delete points
    vector_memory.collections[collection_id].delete_points_by_metadata_filter(metadata)

    return {
        "deleted": []  # TODO: Qdrant does not return deleted points?
    }


# GET all the points from a single collection
@router.get("/collections/{collection_id}/points")
async def get_points_in_collection(
    request: Request,
    collection_id: str,
    limit: int=Query(
        default=100,
        description="How many points to return"
    ),
    offset: str = Query(
        default=None,
        description="If provided (or not empty string) - skip points with ids less than given `offset`"
    ),
    cat: StrayCat = check_permissions(AuthResource.MEMORY, AuthPermission.READ),
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
    collections = list(cat.memory.vectors.collections.keys())
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
    
    memory_collection = cat.memory.vectors.collections[collection_id]
    points, next_offset = memory_collection.get_all_points(limit=limit, offset=offset)
    
    return {
        "points": points,
        "next_offset": next_offset
    }



# EDIT a point in memory
@router.put("/collections/{collection_id}/points/{point_id}", response_model=MemoryPoint)
async def edit_memory_point(
    request: Request,
    collection_id: str,
    point_id: str,
    point: MemoryPointBase,
    cat: StrayCat = check_permissions(AuthResource.MEMORY, AuthPermission.EDIT),
) -> MemoryPoint:
    """Edit a point in memory

    
    Example
    ----------
    ```
    
    collection = "declarative"
    content = "MIAO!"
    metadata = {"custom_key": "custom_value"}
    req_json = {
        "content": content,
        "metadata": metadata,
    }
    # create a point
    res = requests.post(
        f"http://localhost:1865/memory/collections/{collection}/points", json=req_json
    )
    json = res.json()
    #get the id
    point_id = json["id"]
    # new point values
    content = "NEW MIAO!"
    metadata = {"custom_key": "new_custom_value"}
    req_json = {
        "content": content,
        "metadata": metadata,
    }

    # edit the point
    res = requests.put(
        f"http://localhost:1865/memory/collections/{collection}/points/{point_id}", json=req_json
    )
    json = res.json()
    print(json)
    ```
    """

    # do not touch procedural memory
    if collection_id == "procedural":
        raise HTTPException(
            status_code=400, detail={"error": "Procedural memory is read-only."}
        )

    vector_memory: VectorMemory = cat.memory.vectors
    collections = list(vector_memory.collections.keys())
    if collection_id not in collections:
        raise HTTPException(
            status_code=400, detail={"error": "Collection does not exist."}
        )

    #ensure point exist
    points = vector_memory.collections[collection_id].get_points([point_id])
    if points is None or len(points) == 0:
        raise HTTPException(
            status_code=400, detail={"error": "Point does not exist."}
        )

    # embed content
    embedding = cat.embedder.embed_query(point.content)

    # ensure source is set
    if not point.metadata.get("source"):
        point.metadata["source"] = (
            cat.user_id
        )  # this will do also for declarative memory

    # ensure when is set
    if not point.metadata.get("when"):
        point.metadata["when"] = time.time() #if when is not in the metadata set the current time

    # edit point
    qdrant_point = vector_memory.collections[collection_id].add_point(
        content=point.content, vector=embedding, metadata=point.metadata, id=point_id
    )

    return MemoryPoint(
        metadata=qdrant_point.payload["metadata"],
        content=qdrant_point.payload["page_content"],
        vector=qdrant_point.vector,
        id=qdrant_point.id,
    )