from pydantic import BaseModel

from cat.mad_hatter.decorators import endpoint
from cat.auth.permissions import AuthPermission, AuthResource, check_permissions

class Item(BaseModel):
    name: str
    description: str

@endpoint.endpoint(path="/endpoint", methods=["GET"])
def test_endpoint():
    return {"result":"endpoint default prefix"}

@endpoint.endpoint(path="/endpoint", prefix="/tests", methods=["GET"], tags=["Tests"])
def test_endpoint_prefix():
    return {"result":"endpoint prefix tests"}

# from this one on endpoints are secured with permissions checks
@endpoint.get(path="/crud", prefix="/tests", tags=["Tests"])
def test_get(cat=check_permissions(AuthResource.PLUGINS, AuthPermission.LIST)):
    return {"result":"ok", "user_id":cat.user_id}

@endpoint.post(path="/crud", prefix="/tests", tags=["Tests"])
def test_post(
    item: Item,
    cat=check_permissions(AuthResource.PLUGINS, AuthPermission.EDIT)
):
    return {"id": 1, "name": item.name, "description": item.description}

@endpoint.put(path="/crud/{item_id}", prefix="/tests", tags=["Tests"])
def test_put(
    item_id: int,
    item: Item,
    cat=check_permissions(AuthResource.PLUGINS, AuthPermission.WRITE)
):
    return {"id": item_id, "name": item.name, "description": item.description}

@endpoint.delete(path="/crud/{item_id}", prefix="/tests", tags=["Tests"]) 
def test_delete(
    item_id: int,
    cat=check_permissions(AuthResource.PLUGINS, AuthPermission.DELETE)
):
    return {"result": "ok", "deleted_id": item_id}