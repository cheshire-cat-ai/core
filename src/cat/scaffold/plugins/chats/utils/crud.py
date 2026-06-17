from typing import List, Optional
import json
from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from piccolo.table import Table

from cat.auth import User, get_user
from .schemas import Page


def create_crud(
    db_model: Table,
    prefix: str,
    tag: str,
    role: str | None = None,
    select_schema: BaseModel = None,
    create_schema: BaseModel = None,
    update_schema: BaseModel = None,
    restrict_by_user_id: bool = False,
    search_fields: List[str] = [],
) -> APIRouter:
    """Build a generic REST CRUD router over a piccolo `Table`.

    Generic on purpose: it knows nothing about chats. Point it at any
    `UserScopedDB` table and pass the pydantic schemas for select/create/update.
    """

    DBModel = db_model
    SelectSchema, CreateSchema, UpdateSchema = select_schema, create_schema, update_schema

    router = APIRouter(prefix=prefix, tags=[tag])

    @router.get("", description=f"List and search {tag}")
    async def get_list(
        search: Optional[str] = Query(None, description="Search query"),
        user: User = get_user(role=role),
    ) -> Page[SelectSchema]:

        if restrict_by_user_id:
            q = DBModel.objects().where(DBModel.user_id == user.id)
        else:
            q = DBModel.objects()

        q = q.order_by(DBModel.updated_at, ascending=False)
        objs = await q.limit(1000).output(load_json=True)

        if search:
            results = []
            # piccolo + sqlite does not handle search in JSON
            for p in objs:
                content = "".join(json.dumps(getattr(p, sf)).lower() for sf in search_fields)
                if search.lower() in content:
                    results.append(p)
                    if len(results) >= 10:
                        break
            objs = results
        else:
            objs = objs[:10]

        return Page(items=objs, cursor="")

    @router.get("/{id}", description=f"Get a {tag}")
    async def get_one(
        id: str,
        user: User = get_user(role=role),
    ) -> SelectSchema:

        q = DBModel.objects().where(DBModel.id == id)
        if restrict_by_user_id:
            q = q.where(DBModel.user_id == user.id)

        obj = await q.first().output(load_json=True)
        if obj is None:
            raise HTTPException(status_code=404, detail="Not found.")
        return obj

    @router.post("", description=f"Create new {tag}")
    async def create(
        data: CreateSchema = Body(...),
        user: User = get_user(role=role),
    ) -> SelectSchema:

        payload = data.model_dump()
        if restrict_by_user_id:
            payload["user_id"] = user.id
        obj = DBModel(**payload)
        await obj.save()

        return obj

    @router.put("/{id}", description=f"Edit a {tag}")
    async def edit(
        id: str,
        data: UpdateSchema = Body(...),
        user: User = get_user(role=role),
    ) -> SelectSchema:

        q = DBModel.objects().where(DBModel.id == id)
        if restrict_by_user_id:
            q = q.where(DBModel.user_id == user.id)

        obj = await q.first().output(load_json=True)

        if obj is None:
            raise HTTPException(status_code=404, detail=f"{tag} not found.")

        for key, value in data.model_dump().items():
            setattr(obj, key, value)
        await obj.save()

        return obj

    @router.delete("/{id}")
    async def delete(
        id: str,
        user: User = get_user(role=role),
    ):

        q = DBModel.objects().where(DBModel.id == id)
        if restrict_by_user_id:
            q = q.where(DBModel.user_id == user.id)

        obj = await q.first()

        if obj is None:
            raise HTTPException(status_code=404, detail=f"{tag} not found.")

        await obj.remove()

    return router
