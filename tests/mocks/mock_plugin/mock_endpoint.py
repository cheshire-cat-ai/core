from pydantic import BaseModel

from cat import endpoint, user

class Item(BaseModel):
    name: str
    description: str

@endpoint.get(path="/endpoint")
def test_endpoint():
    return {"result":"endpoint default prefix"}

@endpoint.get(path="/endpoint", prefix="/tests", tags=["Tests"])
def test_endpoint_prefix():
    return {"result":"endpoint prefix tests"}

# from this one on endpoints are secured with the `role=` sugar; the authed
# user is read ambiently via `from cat import user`.
@endpoint.get(path="/crud", prefix="/tests", tags=["Tests"], role="admin")
def test_get():
    return {"result":"ok", "user_id": str(user.id)}

@endpoint.post(path="/crud", prefix="/tests", tags=["Tests"], role="admin")
def test_post(item: Item):
    return {"id": 1, "name": item.name, "description": item.description}

@endpoint.put(path="/crud/{item_id}", prefix="/tests", tags=["Tests"], role="admin")
def test_put(item_id: int, item: Item):
    return {"id": item_id, "name": item.name, "description": item.description}

@endpoint.delete(path="/crud/{item_id}", prefix="/tests", tags=["Tests"], role="admin")
def test_delete(item_id: int):
    return {"result": "ok", "deleted_id": item_id}

@endpoint.get(path="/role", prefix="/tests", tags=["Tests"], role="custom")
def test_custom_role():
    return {"result": "ok"}
