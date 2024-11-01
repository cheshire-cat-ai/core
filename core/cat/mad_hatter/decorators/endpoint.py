from typing import Callable
from fastapi import APIRouter

cheshire_cat_api = None

# class to represent a @endpoint
class CustomEndpoint:
    def __init__(self, prefix: str, path: str, function: Callable, **kwargs):
        self.prefix = prefix
        self.path = path
        self.function = function
        self.name = self.prefix + self.path

        for k in kwargs:
            setattr(self, k, kwargs[k])

    def __repr__(self) -> str:
        return f"CustomEndpoint(path={self.name})"

# Called from madhatter to inject the fastapi app instance
def _init_endpoint_decorator(new_cheshire_cat_api):
    global cheshire_cat_api

    cheshire_cat_api = new_cheshire_cat_api

# @endpoint decorator. Any function in a plugin decorated by @endpoint will be exposed as FastAPI operation
def endpoint(path, methods, prefix="/custom_endpoints", tags=["custom_endpoints"], **kwargs) -> Callable:
    """
    Define a custom API endpoint, parameters are the same as FastAPI path operation.
    Examples:
        .. code-block:: python
            @endpoint(path="/hello", methods=["GET"])
            def my_endpoint() -> str:
                return {"Hello":"Alice"}
    """

    global cheshire_cat_api

    def _make_endpoint(endpoint):
        custom_endpoint = CustomEndpoint(prefix=prefix, path=path, function=endpoint, **kwargs)

        plugins_router = APIRouter()
        plugins_router.add_api_route(
            path=path, endpoint=endpoint, methods=methods, tags=tags, **kwargs
        )

        cheshire_cat_api.include_router(plugins_router, prefix=prefix)

        return custom_endpoint

    return _make_endpoint

# @get_endpoint decorator. Any function in a plugin decorated by @endpoint will be exposed as FastAPI GET operation
def get_endpoint(
    path, prefix="/custom_endpoints", response_model=None, tags=["custom_endpoints"], **kwargs
) -> Callable:
    """
    Define a custom API endpoint for GET operation, parameters are the same as FastAPI path operation.
    Examples:
        .. code-block:: python
            @get_endpoint(path="/hello")
            def my_get_endpoint() -> str:
                return {"Hello":"Alice"}
    """

    return endpoint(
        path=path,
        methods=["GET"],
        prefix=prefix,
        response_model=response_model,
        tags=tags,
        **kwargs,
    )

# @post_endpoint decorator. Any function in a plugin decorated by @endpoint will be exposed as FastAPI POST operation
def post_endpoint(
    path, prefix="/custom_endpoints", response_model=None, tags=["custom_endpoints"], **kwargs
) -> Callable:

    """
    Define a custom API endpoint for POST operation, parameters are the same as FastAPI path operation.
    Examples:
        .. code-block:: python

            from pydantic import BaseModel

            class Item(BaseModel):
                name: str
                description: str

            @post_endpoint(path="/hello")
            def my_post_endpoint(item: Item) -> str:
                return {"Hello": item.name, "Description": item.description}
    """
    return endpoint(
        path=path,
        methods=["POST"],
        prefix=prefix,
        response_model=response_model,
        tags=tags,
        **kwargs,
    )
