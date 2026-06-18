
from importlib.metadata import metadata
from fastapi import FastAPI, APIRouter, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse

router = APIRouter()

FAVICON = "https://cheshirecat.ai/wp-content/uploads/2023/10/Logo-Cheshire-Cat.svg"
RAPIDOC_JS = "https://unpkg.com/rapidoc/dist/rapidoc-min.js"


# Endpoint playground
@router.get("/docs", include_in_schema=False)
async def swagger_docs(r: Request):
    r.app.openapi = get_openapi_configuration_function(r.app)
    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{r.app.title}</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <link rel="icon" href="{FAVICON}" />
            <script type="module" src="{RAPIDOC_JS}"></script>
        </head>
        <body>
            <!--
              RapiDoc playground.
              - fetch-credentials="include": "Try" requests send the browser's
                httponly `access_token` cookie (run in the top window), so a
                logged-in session "just works" with nothing to paste.
              - The "Authentication" nav item is a single global box to paste the
                master API key / a JWT once; it's then applied to every call.
            -->
            <rapi-doc
                spec-url="/openapi.json"
                render-style="view"
                show-header="false"
                allow-authentication="true"
                allow-server-selection="false"
                fetch-credentials="include"
                theme="light"
                primary-color="#e6007e"
                regular-font="system-ui, sans-serif"
            >
                <img slot="logo" src="{FAVICON}" style="height:32px;width:auto;" />
            </rapi-doc>
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

        # Auth now happens in the context middleware, not via a FastAPI security
        # dependency, so FastAPI no longer emits this on its own. Declare it by
        # hand so /docs shows the "Authorize" form: paste the master API key or a
        # JWT and it's sent as `Authorization: Bearer <credential>` (see Auth.get_credential).
        # The session cookie is handled separately by the requestInterceptor in
        # /docs (httponly cookies can't be set from the Authorize dialog).
        openapi_schema.setdefault("components", {})["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Master API key or a core-signed JWT.",
            },
        }
        openapi_schema["security"] = [{"BearerAuth": []}]

        cheshire_cat_api.openapi_schema = openapi_schema
        return cheshire_cat_api.openapi_schema

    return custom_openapi
