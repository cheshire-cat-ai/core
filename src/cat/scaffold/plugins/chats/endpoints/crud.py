"""Chats REST API.

Plain `@endpoint` handlers — no generic router factory. Each route is gated with
the `role="authenticated"` sugar and reads the current user ambiently via
`from cat import user`, scoping every row by `user.id`.
"""

import json
from typing import List, Dict, Optional

from fastapi import Body, Query, HTTPException

from cat import endpoint, user
from cat.types import Message

from ..db import ChatDB
from ..utils.schemas import Page, CRUDSelect, CRUDUpdate


class ChatCreateUpdate(CRUDUpdate):
    messages: List[Message] = []
    context: Dict = {}


class ChatSelect(CRUDSelect):
    messages: List[Message]
    context: Dict


SEARCH_FIELDS = ["name", "messages", "context"]


@endpoint.get("/chats", tags=["Chats"], role="authenticated")
async def list_chats(
    search: Optional[str] = Query(None, description="Search query"),
) -> Page[ChatSelect]:
    q = (
        ChatDB.objects()
        .where(ChatDB.user_id == user.id)
        .order_by(ChatDB.updated_at, ascending=False)
    )
    objs = await q.limit(1000).output(load_json=True)

    if search:
        results = []
        # piccolo + sqlite does not handle search in JSON
        for p in objs:
            content = "".join(json.dumps(getattr(p, sf)).lower() for sf in SEARCH_FIELDS)
            if search.lower() in content:
                results.append(p)
                if len(results) >= 10:
                    break
        objs = results
    else:
        objs = objs[:10]

    return Page(items=objs, cursor="")


@endpoint.get("/chats/{id}", tags=["Chats"], role="authenticated")
async def get_chat(id: str) -> ChatSelect:
    obj = await (
        ChatDB.objects()
        .where(ChatDB.id == id)
        .where(ChatDB.user_id == user.id)
        .first()
        .output(load_json=True)
    )
    if obj is None:
        raise HTTPException(status_code=404, detail="Not found.")
    return obj


@endpoint.post("/chats", tags=["Chats"], role="authenticated")
async def create_chat(data: ChatCreateUpdate = Body(...)) -> ChatSelect:
    obj = ChatDB(**data.model_dump(), user_id=user.id)
    await obj.save()
    return obj


@endpoint.put("/chats/{id}", tags=["Chats"], role="authenticated")
async def edit_chat(id: str, data: ChatCreateUpdate = Body(...)) -> ChatSelect:
    obj = await (
        ChatDB.objects()
        .where(ChatDB.id == id)
        .where(ChatDB.user_id == user.id)
        .first()
        .output(load_json=True)
    )
    if obj is None:
        raise HTTPException(status_code=404, detail="Chat not found.")

    for key, value in data.model_dump().items():
        setattr(obj, key, value)
    await obj.save()
    return obj


@endpoint.delete("/chats/{id}", tags=["Chats"], role="authenticated")
async def delete_chat(id: str):
    obj = await (
        ChatDB.objects()
        .where(ChatDB.id == id)
        .where(ChatDB.user_id == user.id)
        .first()
    )
    if obj is None:
        raise HTTPException(status_code=404, detail="Chat not found.")
    await obj.remove()
