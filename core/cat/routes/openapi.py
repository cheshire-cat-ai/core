import os

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

API_KEY = os.getenv("API_KEY")


def get_openapi_configuration_function(cheshire_cat_api: FastAPI):
    # Configure openAPI schema for swagger and redoc
    def custom_openapi():
        if cheshire_cat_api.openapi_schema:
            return cheshire_cat_api.openapi_schema

        openapi_schema = get_openapi(
            title="😸 Cheshire-Cat API",
            version="0.1 (beta)",
            description="Customizable AI architecture",
            routes=cheshire_cat_api.routes,
        )

        # Image should be an url and it's mostly used for redoc
        openapi_schema["info"]["x-logo"] = {
            "url": "https://github.com/pieroit/cheshire-cat/blob/main/cheshire-cat.jpeg?raw=true"
        }

        # force security None on endpoints if API_KEY is not present
        if not API_KEY:
            openapi_schema["components"]["securitySchemes"] = None

            paths = openapi_schema["paths"]
            for _, path in paths.items():
                for __, verb in path.items():
                    verb["security"] = None  # default is [{'APIKeyHeader': []}]

        cheshire_cat_api.openapi_schema = openapi_schema
        return cheshire_cat_api.openapi_schema

    return custom_openapi
