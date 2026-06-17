from typing import List, Dict

from cat import endpoint
from cat.types import Message
from ..utils.crud import create_crud
from ..utils.schemas import CRUDSelect, CRUDUpdate

from ..db import ChatDB


class ChatCreateUpdate(CRUDUpdate):
    messages: List[Message] = []
    context: Dict = {}


class ChatSelect(CRUDSelect):
    messages: List[Message]
    context: Dict


@endpoint.router
def chats_crud():
    router = create_crud(
        db_model=ChatDB,
        prefix="/chats",
        tag="Chats",
        restrict_by_user_id=True,
        search_fields=["name", "messages", "context"],
        select_schema=ChatSelect,
        create_schema=ChatCreateUpdate,
        update_schema=ChatCreateUpdate,
    )
    return router
