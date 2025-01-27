from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import tomli



def get_openapi_configuration_function(cheshire_cat_api: FastAPI):
    # Configure openAPI schema for swagger and redoc
    def custom_openapi():
        if cheshire_cat_api.openapi_schema:
            return cheshire_cat_api.openapi_schema

        with open("pyproject.toml", "rb") as f:
            project_toml = tomli.load(f)["project"]

        openapi_schema = get_openapi(
            title=f"😸 {project_toml['name']} API",
            version=project_toml["version"],
            description=project_toml["description"],
            routes=cheshire_cat_api.routes,
        )

        # Image should be an url and it's mostly used for redoc
        openapi_schema["info"]["x-logo"] = {
            "url": "https://cheshirecat.ai/wp-content/uploads/2023/10/Logo-Cheshire-Cat.svg"  # TODO: update with logo
        }

        # force security None on endpoints if API_KEY is not present
        # API_KEY = get_env("CCAT_API_KEY")
        # if not API_KEY:
        #    openapi_schema["components"]["securitySchemes"] = None

        #    paths = openapi_schema["paths"]
        #    for _, path in paths.items():
        #        for __, verb in path.items():
        #            verb["security"] = None  # default is [{'APIKeyHeader': []}]

        cheshire_cat_api.openapi_schema = openapi_schema
        return cheshire_cat_api.openapi_schema

    return custom_openapi
