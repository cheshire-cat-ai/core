
from importlib.metadata import metadata
from fastapi import FastAPI, APIRouter, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse

router = APIRouter()

SCALAR_FAVICON = "https://cheshirecat.ai/wp-content/uploads/2023/10/Logo-Cheshire-Cat.svg"

# Endpoint playground
@router.get("/docs", include_in_schema=False)
async def scalar_docs(r: Request):
    r.app.openapi = get_openapi_configuration_function(r.app)
    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{r.app.title}</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <link rel="icon" href="{SCALAR_FAVICON}" />
        </head>
        <body>
            <script id="api-reference" data-url="/openapi.json"></script>
            <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
        </body>
        </html>
        """
    )

def get_openapi_configuration_function(cheshire_cat_api: FastAPI):
    # Configure openAPI schema for swagger and redoc
    def custom_openapi():
        if cheshire_cat_api.openapi_schema:
            return cheshire_cat_api.openapi_schema

        meta = metadata("cheshire-cat-ai")

        openapi_schema = get_openapi(
            title=f"🐱 Cheshire Cat AI - {meta.get('version')}",
            version=meta.get("version", "unknown"),
            description=meta.get("Summary"),
            routes=cheshire_cat_api.routes,
            external_docs={
                "description": "Cheshire Cat AI Documentation",
                "url": "https://cheshire-cat-ai.github.io/docs/",
            }
        )

        cheshire_cat_api.openapi_schema = openapi_schema
        return cheshire_cat_api.openapi_schema

    return custom_openapi
