from pydantic import BaseModel
from typing import List
from uuid import uuid4

from fastapi import Depends, APIRouter, HTTPException

from cat.log import log
from cat.db import models
from cat.db import crud
from cat.auth.utils import AuthPermission, AuthResource
from cat.auth.headers import http_auth

# users dict dependency injection
#def users_db():
#    return crud.get_users()

router = APIRouter()

class UserBase(BaseModel):
    username: str
    permissions: List[str] = []

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    username: str

class UserResponse(UserBase):
    id: str

@router.post("/", response_model=UserResponse)
def create_user(
    new_user: UserCreate,
    users_db = Depends(crud.get_users),
    stray=Depends(http_auth(AuthResource.USERS, AuthPermission.WRITE)),
):
    new_id = str(uuid4())
    users_db[new_id] = {
        "id": new_id,
        **new_user.model_dump()
    }
    crud.update_users(users_db)
    return users_db[new_id]

@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    users_db = Depends(crud.get_users),
    stray=Depends(http_auth(AuthResource.USERS, AuthPermission.LIST)),
):
    users = list(users_db.values())[skip: skip + limit]
    return users

@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: str,
    users_db = Depends(crud.get_users),
    stray=Depends(http_auth(AuthResource.USERS, AuthPermission.READ)),
):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail={"error": "User not found"})
    return users_db[user_id]

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user: UserUpdate,
    users_db = Depends(crud.get_users),
    stray=Depends(http_auth(AuthResource.USERS, AuthPermission.EDIT)),
):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail={"error": "User not found"})
    stored_user = users_db[user_id]
    updated_user = stored_user | user.model_dump(exclude_unset=True)
    users_db[user_id] = updated_user
    crud.update_users(users_db)
    return updated_user

@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(
    user_id: str,
    users_db = Depends(crud.get_users),
    stray=Depends(http_auth(AuthResource.USERS, AuthPermission.DELETE)),
):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail={"error": "User not found"})
    user = users_db.pop(user_id)
    crud.update_users(users_db)
    return user
