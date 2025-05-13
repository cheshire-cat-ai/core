

from typing import Dict
from fastapi import Request, APIRouter, HTTPException
from pydantic import BaseModel

from cat.auth.permissions import AuthPermission, AuthResource, check_permissions
from cat.looking_glass.stray_cat import StrayCat
from cat.convo.messages import ConversationMessage, Role, CatMessage, UserMessage


router = APIRouter()

# DELETE conversation history from working memory
@router.delete("/conversation_history")
async def wipe_conversation_history(
    request: Request,
    cat: StrayCat = check_permissions(AuthResource.MEMORY, AuthPermission.DELETE),
) -> Dict:
    """Delete the specified user's conversation history from working memory"""

    cat.working_memory.history = []

    return {
        "deleted": True,
    }


# GET conversation history from working memory
@router.get("/conversation_history")
async def get_conversation_history(
    request: Request,
    cat: StrayCat = check_permissions(AuthResource.MEMORY, AuthPermission.READ),
) -> Dict:
    """Get the specified user's conversation history from working memory"""

    return {"history": cat.working_memory.history}


# PUT conversation history from working memory
@router.put("/conversation_history/{conversation_history_index}")
async def put_conversation_history(
    request: Request,
    conversation_history_index: int,
    history_message: ConversationMessage,
    stray: StrayCat = check_permissions(AuthResource.MEMORY, AuthPermission.EDIT),
) -> Dict:
    """Edit a conversation history in working memory in a specified index. Supports negative indexing for reverse access.
    
    Example
    ----------
    ```
    # overwrite last history message
    req_json = {
        "who": "Human",
        "text": "MIAO!",
        "user_id": "123"
    }
    res = requests.put(
        "http://localhost:1865/memory/conversation_history/-1", json=req_json
    )

    # overwrite first history message
    req_json = requests.get("http://localhost:1865/memory/conversation_history")
    req_json = req_json.json()["history"][0]

    req_json["text"] = "MIAO!"
    res = requests.put(
        "http://localhost:1865/memory/conversation_history/0", json=req_json
    )
    ```
    """

    working_memory = stray.working_memory 
    history = working_memory.history

    if conversation_history_index < -len(history) or conversation_history_index >= len(history):
        raise HTTPException(
            status_code=400, detail={"error": f"Invalid conversation history index. Index out of range. Please use a valid -{len(working_memory.history)} < index < {len(working_memory.history)}."}
        )
    
    if history_message.who == Role.AI:
        history_message = CatMessage(**history_message.model_dump())
    else:
        history_message = UserMessage(**history_message.model_dump())

    working_memory.update_history(history_message, conversation_history_index)

    # if conversation_history_index is None return the last message in the history
    if conversation_history_index is None:
        conversation_history_index = -1

    return history[conversation_history_index].model_dump()