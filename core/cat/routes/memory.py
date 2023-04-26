from fastapi import Query, Request, APIRouter
from typing import Dict

router = APIRouter()


# DELETE delete_memories
@router.delete("/{memory_id}/")
async def delete_memories(memory_id: str) -> Dict:
    """
    Delete specific memory.

    :param memory_id: ID of the memory
    :type memory_id: str
    :return: {"error": "to be implemented"}
    :rtype: Dict
    """
    return {"error": "to be implemented"}


# GET recall_memories
@router.get("/recall/")
async def recall_memories_from_text(
    request: Request,
    text: str = Query(description="Find memories similar to this text."),
    k: int = Query(default=100, description="How many memories to return."),
) -> Dict:
    """
    Search k memories similar to given text

    :param request: Request
    :type request: Request
    :param text: Text, defaults to Query(description="Find memories similar to this text.")
    :type text: str, optional
    :param k: Number of memories to return, defaults to Query(default=100, description="How many memories to return.")
    :type k: int, optional
    :return: {"episodes": episodes, "documents": documents},
    :rtype: Dict
    """

    ccat = request.app.state.ccat
    vector_memory = ccat.memory.vectors

    episodes = vector_memory.episodic.recall_memories_from_text(text=text, k=k)
    documents = vector_memory.declarative.recall_memories_from_text(text=text, k=k)

    episodes = [dict(m[0]) | {"score": float(m[1])} for m in episodes]
    documents = [dict(m[0]) | {"score": float(m[1])} for m in documents]

    return (
        {
            "episodes": episodes,
            "documents": documents,
        },
    )
