from typing import Literal
from fastmcp.client import auth as mcp_auth
from pydantic import BaseModel, HttpUrl, field_serializer

from cat import utils


class MCPServer(BaseModel):
    name: str
    description: str
    url: HttpUrl
    auth_type: Literal["oauth2", "apikey", "none"] = "none"

    @field_serializer("url")
    def serialize_url(self, url):
        return str(url)

    async def to_fastmcp_auth(self, cat):
        if self.auth_type == "apikey":
            return mcp_auth.BearerAuth(
                token=self.token # TODOV2: take it from DB
            )
        elif self.auth_type == "oauth2":
            # TODOV2: take info from DB
            return mcp_auth.OAuth(
                mcp_url=self.url,
                scopes=self.scopes,
                client_name="Cheshire Cat AI",
                additional_client_metadata=self.additional_client_metadata,
                token_storage_cache_dir = utils.get_data_path(), # should be per user
                callback_port = 1866, # TODOV2: remember to open it in the docker
            )
        else:
            return self.url
