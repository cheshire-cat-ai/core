
from fastapi import Depends, Request, Response, APIRouter, HTTPException, status
from fastapi import FastAPI, WebSocket, UploadFile, BackgroundTasks, Body, Query


router = APIRouter()


# DELETE delete_memories
@router.delete("/{memory_id}/")
async def delete_memories(memory_id: str):
    """Delete specific memory. 
    """
    return {"error": "to be implemented"}


# GET recall_memories
@router.get("/recall/")
async def recall_memories_from_text(
        request: Request,
        text: str = Query(description="Find memories similar to this text."),
        k: int = Query(default=100, description="How many memories to return."),
    ):
    """Search k memories similar to given text. 
    """

    ccat = request.app.state.ccat

    memories = ccat.recall_memories_from_text(
        text=text, collection="episodes", k=k
    )
    documents = ccat.recall_memories_from_text(
        text=text, collection="documents", k=k
    )

    memories = [dict(m[0]) | {"score": float(m[1])} for m in memories]
    documents = [dict(m[0]) | {"score": float(m[1])} for m in documents]

    return (
        {
            "memories": memories,
            "documents": documents,
        },
    )