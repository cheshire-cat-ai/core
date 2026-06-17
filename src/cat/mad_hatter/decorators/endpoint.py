from typing import Callable
from fastapi import APIRouter


class Endpoint(APIRouter):

    def __repr__(self) -> str:
        if hasattr(self, 'plugin_id'):
            plugin = self.plugin_id # will be added by mad hatter
        else:
            plugin = "unkwown"
        return f"Endpoint(plugin={plugin} routes={self.routes})"


class EndpointDecorator:

    def _wrap(self, method: str, path: str, **kwargs):

        def decorator(func: Callable):
            
            prefix = kwargs.pop("prefix", "")
            full_path = f"{prefix}{path}"

            router = Endpoint()
            router.add_api_route(
                path=full_path,
                endpoint=func,
                methods=[method.upper()],
                **kwargs
            )

            return router
        return decorator

    def get(self, path: str, **kwargs):
        return self._wrap("get", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self._wrap("post", path, **kwargs)

    def put(self, path: str, **kwargs):
        return self._wrap("put", path, **kwargs)
    
    def patch(self, path: str, **kwargs):
        return self._wrap("patch", path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self._wrap("delete", path, **kwargs)
    
    def router(self, function: Callable):

        # TODOV2: support async functions
        returned_router = function()

        if not isinstance(returned_router, APIRouter):
            raise TypeError(
                "The function decorated with @endpoint.router must return an APIRouter instance."
            )

        ce = Endpoint()
        ce.include_router(returned_router)
        return ce

# TODOV2: endpoints with the same function name collide, even with different paths

endpoint = EndpointDecorator()