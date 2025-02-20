from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict
from uuid import uuid4

from fastapi import Depends, APIRouter, HTTPException

from cat.db import crud
from cat.auth.permissions import AuthPermission, AuthResource, get_base_permissions, check_permissions
from cat.auth.auth_utils import hash_password

router = APIRouter()

class UserBase(BaseModel):
    username: str = Field(min_length=2)
    permissions: Dict[AuthResource, List[AuthPermission]] = get_base_permissions()

class UserCreate(UserBase):
    password: str = Field(min_length=5)
    # no additional fields allowed
    model_config: ConfigDict = {"extra": "forbid"}

class UserUpdate(UserBase):
    username: str = Field(default=None, min_length=2)
    password: str = Field(default=None, min_length=4)
    permissions: Dict[AuthResource, List[AuthPermission]] = None
    model_config: ConfigDict = {"extra": "forbid"}

class UserResponse(UserBase):
    id: str

@router.post("/", response_model=UserResponse)
def create_user(
    new_user: UserCreate,
    users_db = Depends(crud.get_users),
    cat=check_permissions(AuthResource.USERS, AuthPermission.WRITE),
):
    # check for user duplication with shameful loop
    for id, u in users_db.items():
        if u["username"] == new_user.username:
            raise HTTPException(
                status_code=403,
                detail={"error": "Cannot duplicate user"}
            )
        
    #hash password
    new_user.password = hash_password(new_user.password)
        
    # create user
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
    cat=check_permissions(AuthResource.USERS, AuthPermission.LIST),
):
    users = list(users_db.values())[skip: skip + limit]
    return users

@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: str,
    users_db = Depends(crud.get_users),
    cat=check_permissions(AuthResource.USERS, AuthPermission.READ),
):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail={"error": "User not found"})
    return users_db[user_id]

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user: UserUpdate,
    users_db = Depends(crud.get_users),
    cat=check_permissions(AuthResource.USERS, AuthPermission.EDIT),
):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail={"error": "User not found"})
    
    stored_user = users_db[user_id]
    if user.password:
        user.password = hash_password(user.password)
    updated_user = stored_user | user.model_dump(exclude_unset=True)
    users_db[user_id] = updated_user
    crud.update_users(users_db)
    return updated_user

@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(
    user_id: str,
    users_db = Depends(crud.get_users),
    cat=check_permissions(AuthResource.USERS, AuthPermission.DELETE),
):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail={"error": "User not found"})
    
    user = users_db.pop(user_id)
    crud.update_users(users_db)
    return user
