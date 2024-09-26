from typing import Dict
from fastapi import Request, APIRouter, HTTPException, Depends

from cat.looking_glass.cheshire_cat import CheshireCat
from cat.auth.connection import HTTPAuth
from cat.auth.permissions import AuthPermission, AuthResource
from cat.memory.vector_memory import VectorMemory
from cat.looking_glass.stray_cat import StrayCat
from cat import utils

router = APIRouter()

# GET collection list with some metadata
@router.get("/collections")
async def get_collections(
    request: Request,
    stray: StrayCat = Depends(HTTPAuth(AuthResource.MEMORY, AuthPermission.READ))
) -> Dict:
    """Get list of available collections"""
    
    vector_memory: VectorMemory = stray.memory.vectors
    collections = list(vector_memory.collections.keys())
    
    collections_metadata = []
    for c in collections:
        coll_meta = vector_memory.get_collection(c)
        collections_metadata.append({
            "name": c,
            "vectors_count": coll_meta.points_count
        })

    return {"collections": collections_metadata}


# DELETE all collections
@router.delete("/collections")
async def wipe_collections(
    request: Request,
    stray: StrayCat = Depends(HTTPAuth(AuthResource.MEMORY, AuthPermission.DELETE)),
) -> Dict:
    """Delete and create all collections"""

    vector_memory: VectorMemory = stray.memory.vectors
    deleted_memories = utils.delete_collections(vector_memory)

    ccat: CheshireCat = request.app.state.ccat
    ccat.load_memory()  # recreate the long term memories
    ccat.mad_hatter.find_plugins()

    return {
        "deleted": deleted_memories,
    }


# DELETE one collection
@router.delete("/collections/{collection_id}")
async def wipe_single_collection(
    request: Request,
    collection_id: str,
    stray: StrayCat = Depends(HTTPAuth(AuthResource.MEMORY, AuthPermission.DELETE)),
) -> Dict:
    """Delete and recreate a collection"""

    vector_memory: VectorMemory = stray.memory.vectors
    collections = list(vector_memory.collections.keys())
    
    if collection_id not in collections:
        raise HTTPException(
            status_code=400, detail={"error": "Collection does not exist."}
        )

    to_return = {}
    ret = vector_memory.delete_collection(collection_id)
    to_return[collection_id] = ret

    ccat: CheshireCat = request.app.state.ccat
    ccat.load_memory()  # recreate the long term memories
    ccat.mad_hatter.find_plugins()

    return {
        "deleted": to_return,
    }


