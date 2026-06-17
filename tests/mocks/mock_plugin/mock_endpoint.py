from pydantic import BaseModel

from cat.mad_hatter.decorators import endpoint
from cat.auth import get_user, User

class Item(BaseModel):
    name: str
    description: str

@endpoint.endpoint(path="/endpoint", methods=["GET"])
def test_endpoint():
    return {"result":"endpoint default prefix"}

@endpoint.endpoint(path="/endpoint", prefix="/tests", methods=["GET"], tags=["Tests"])
def test_endpoint_prefix():
    return {"result":"endpoint prefix tests"}

# from this one on endpoints are secured with role checks
@endpoint.get(path="/crud", prefix="/tests", tags=["Tests"])
def test_get(user: User = get_user(role="admin")):
    return {"result":"ok", "user_id": str(user.id)}

@endpoint.post(path="/crud", prefix="/tests", tags=["Tests"])
def test_post(
    item: Item,
    user: User = get_user(role="admin")
):
    return {"id": 1, "name": item.name, "description": item.description}

@endpoint.put(path="/crud/{item_id}", prefix="/tests", tags=["Tests"])
def test_put(
    item_id: int,
    item: Item,
    user: User = get_user(role="admin")
):
    return {"id": item_id, "name": item.name, "description": item.description}

@endpoint.delete(path="/crud/{item_id}", prefix="/tests", tags=["Tests"])
def test_delete(
    item_id: int,
    user: User = get_user(role="admin")
):
    return {"result": "ok", "deleted_id": item_id}

@endpoint.get(path="/role", prefix="/tests", tags=["Tests"])
def test_custom_role(
    user: User = get_user(role="custom")
):
    return {"result": "ok"}
