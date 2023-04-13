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
            # TODO: this description should be more descriptive about the APIs capabilities
            description="Customizable AI architecture",
            routes=cheshire_cat_api.routes,
        )
        # Image should be an url and it's mostly used for redoc
        openapi_schema["info"]["x-logo"] = {
            "url": "https://github.com/pieroit/cheshire-cat/blob/main/cheshire-cat.jpeg?raw=true"
        }
        if not API_KEY:
            openapi_schema["components"]["securitySchemes"] = None
            openapi_schema["paths"]["/"]["get"]["security"] = None
            openapi_schema["paths"]["/settings/"]["get"]["security"] = None
            openapi_schema["paths"]["/settings/"]["post"]["security"] = None
            openapi_schema["paths"]["/settings/{settingId}"]["get"]["security"] = None
            openapi_schema["paths"]["/settings/{settingId}"]["delete"][
                "security"
            ] = None
            openapi_schema["paths"]["/settings/{settingId}"]["patch"]["security"] = None
            openapi_schema["paths"]["/settings/llm/"]["get"]["security"] = None
            openapi_schema["paths"]["/settings/llm/{languageModelName}"]["put"][
                "security"
            ] = None
            openapi_schema["paths"]["/settings/embedder/"]["get"]["security"] = None
            openapi_schema["paths"]["/settings/embedder/{languageEmbedderName}"]["put"][
                "security"
            ] = None
            openapi_schema["paths"]["/memory/recall/"]["get"]["security"] = None
            openapi_schema["paths"]["/memory/{memory_id}/"]["delete"]["security"] = None
            openapi_schema["paths"]["/rabbithole/"]["post"]["security"] = None
        # Defines preconfigured examples for swagger
        # This example set parameter of /settings/ get: 'limit' to 3, page to 2 and search to "XYZ"
        # openapi_schema["paths"]["/settings/"]["get"]["parameters"][0]["example"] = 3
        # openapi_schema["paths"]["/settings/"]["get"]["parameters"][1]["example"] = 2
        # openapi_schema["paths"]["/settings/"]["get"]["parameters"][2]["example"] = "XYZ"
        cheshire_cat_api.openapi_schema = openapi_schema
        return cheshire_cat_api.openapi_schema

    return custom_openapi
