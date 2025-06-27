from typing import Callable
from fastapi import APIRouter

from cat.log import log

# class to represent a @endpoint
class CustomEndpoint:
    def __init__(
        self,
        prefix: str,
        path: str,
        function: Callable,
        methods,
        tags,
        **kwargs,
    ):
        self.prefix = prefix
        self.path = path
        self.function = function
        self.tags = tags
        self.methods = methods
        self.kwargs = kwargs
        self.name = self.prefix + self.path

        # fastAPI instance, will be set by the activate method
        self.cheshire_cat_api = None

    def __repr__(self) -> str:
        return f"CustomEndpoint(path={self.name} methods={self.methods})"

    def activate(self, cheshire_cat_api):


        self.cheshire_cat_api = cheshire_cat_api

        # Set the fastapi api_route into the Custom Endpoint
        for api_route in self.cheshire_cat_api.routes:
            if api_route.path == self.name and api_route.methods == self.methods:
                log.warning(f"There is already an active {self.methods} endpoint with path {self.name}")
                return

        log.info(f"Activating custom endpoint {self.methods} {self.name}")
        
        plugins_router = APIRouter()
        plugins_router.add_api_route(
            path=self.path,
            endpoint=self.function,
            methods=self.methods,
            tags=self.tags,
            **self.kwargs,
        )

        try:
            self.cheshire_cat_api.include_router(plugins_router, prefix=self.prefix)
        except Exception:
            log.error(f"Error activating custom endpoint {self.methods} {self.name}")
            return

        self.cheshire_cat_api.openapi_schema = None  # Flush the cache of openapi schema

        # Set the fastapi api_route into the Custom Endpoint
        for api_route in self.cheshire_cat_api.routes:
            if api_route.path == self.name and api_route.methods == self.methods:
                self.api_route = api_route
                break
        
        assert api_route.path == self.name

    def deactivate(self):

        log.info(f"Deactivating custom endpoint {self.methods} {self.name}")

        # Seems there is no official way to remove a route:
        # https://github.com/fastapi/fastapi/discussions/8088
        # https://github.com/fastapi/fastapi/discussions/9855
        if self.cheshire_cat_api:
            to_remove = None
            for api_route in self.cheshire_cat_api.routes:
                if api_route.path == self.name and api_route.methods == self.methods:
                    to_remove = api_route
                    break

            if to_remove:
                self.cheshire_cat_api.routes.remove(api_route)
                self.cheshire_cat_api.openapi_schema = None  # Flush the cached openapi schema

class Endpoint:

    cheshire_cat_api = None

    default_prefix = "/custom"
    default_tags = ["Custom Endpoints"]

    # Called from madhatter to inject the fastapi app instance
    def _init_decorators(cls, new_cheshire_cat_api):
        cls.cheshire_cat_api = new_cheshire_cat_api

    # @endpoint decorator. Any function in a plugin decorated by @endpoint.endpoint will be exposed as FastAPI operation
    def endpoint(
        cls,
        path,
        methods,
        prefix=default_prefix,
        tags=default_tags,
        **kwargs,
    ) -> Callable:
        """
        Define a custom API endpoint, parameters are the same as FastAPI path operation.
        Examples:
            .. code-block:: python
                from cat.mad_hatter.decorators import endpoint

                @endpoint.endpoint(path="/hello", methods=["GET"])
                def my_endpoint():
                    return {"Hello":"Alice"}
        """

        def _make_endpoint(endpoint):
            custom_endpoint = CustomEndpoint(
                prefix=prefix,
                path=path,
                function=endpoint,
                methods=set(methods),
                tags=tags,
                **kwargs,
            )

            return custom_endpoint

        return _make_endpoint

    # Any function in a plugin decorated by @endpoint.get will be exposed as FastAPI GET operation
    def get(
        cls,
        path,
        prefix=default_prefix,
        response_model=None,
        tags=default_tags,
        **kwargs,
    ) -> Callable:
        """
        Define a custom API endpoint for GET operation, parameters are the same as FastAPI path operation.
        Examples:
            .. code-block:: python
                from cat.mad_hatter.decorators import endpoint

                @endpoint.get(path="/hello")
                def my_get_endpoint():
                    return {"Hello":"Alice"}
        """

        return cls.endpoint(
            path=path,
            methods={"GET"},
            prefix=prefix,
            response_model=response_model,
            tags=tags,
            **kwargs,
        )

    # Any function in a plugin decorated by @endpoint.post will be exposed as FastAPI POST operation
    def post(
        cls,
        path,
        prefix=default_prefix,
        response_model=None,
        tags=default_tags,
        **kwargs,
    ) -> Callable:
        """
        Define a custom API endpoint for POST operation, parameters are the same as FastAPI path operation.
        Examples:
            .. code-block:: python

                from cat.mad_hatter.decorators import endpoint
                from pydantic import BaseModel

                class Item(BaseModel):
                    name: str
                    description: str

                @endpoint.post(path="/hello")
                def my_post_endpoint(item: Item):
                    return {"Hello": item.name, "Description": item.description}
        """
        return cls.endpoint(
            path=path,
            methods={"POST"},
            prefix=prefix,
            response_model=response_model,
            tags=tags,
            **kwargs,
        )

    def put(
        cls,
        path,
        prefix=default_prefix,
        response_model=None,
        tags=default_tags,
        **kwargs,
    ) -> Callable:
        """
        Define a custom API endpoint for PUT operation, parameters are the same as FastAPI path operation.
        Examples:
            .. code-block:: python
                from cat.mad_hatter.decorators import endpoint
                from pydantic import BaseModel
    
                class Item(BaseModel):
                    name: str
                    description: str
    
                @endpoint.put(path="/hello")
                def my_put_endpoint(item: Item):
                    return {"Hello": item.name, "Description": item.description}
        """
        return cls.endpoint(
            path=path,
            methods={"PUT"},
            prefix=prefix,
            response_model=response_model,
            tags=tags,
            **kwargs,
        )
    
    def delete(
        cls, 
        path,
        prefix=default_prefix,
        response_model=None,
        tags=default_tags,
        **kwargs,
    ) -> Callable:
        """
        Define a custom API endpoint for DELETE operation, parameters are the same as FastAPI path operation.
        Examples:
            .. code-block:: python
                from cat.mad_hatter.decorators import endpoint
    
                @endpoint.delete(path="/hello/{item_id}")
                def my_delete_endpoint(item_id: int):
                    return {"message": f"Deleted item {item_id}"}
        """
        return cls.endpoint(
            path=path,
            methods={"DELETE"},
            prefix=prefix,
            response_model=response_model,
            tags=tags,
            **kwargs,
        )

endpoint = None

if not endpoint:
    endpoint = Endpoint()
