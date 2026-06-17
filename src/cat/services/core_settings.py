from typing import Type, Literal, TYPE_CHECKING
from pydantic import BaseModel, Field

from cat.services.service import Service
from cat import log

if TYPE_CHECKING:
    from cat.looking_glass.cheshire_cat import CheshireCat


class CoreSettings(Service):
    """Framework-wide installation settings (default LLM, embedder, etc.)."""

    service_type = "config"
    slug = "core"
    name = "Core Settings"
    description = "Framework-wide installation defaults."

    class Settings(BaseModel):
        default_llm: str = "default:default"
        default_embedder: str = "default:default"

    @classmethod
    async def settings_schema(cls, app: "CheshireCat") -> Type[BaseModel]:
        """Dynamic schema: enumerate available LLMs/embedders from all providers."""

        llm_options = ["default:default"]
        embedder_options = ["default:default"]

        for slug in app.registry.classes.get("model_providers", {}):
            try:
                provider = await app.get("model_providers", slug)
                for llm in await provider.list_llms():
                    llm_options.append(f"{slug}:{llm}")
                for emb in await provider.list_embedders():
                    embedder_options.append(f"{slug}:{emb}")
            except Exception as e:
                log.error(f"Error querying model provider {slug}: {e}")

        LLMEnum = Literal[tuple(llm_options)]
        EmbedderEnum = Literal[tuple(embedder_options)]

        class DynamicSettings(BaseModel):
            default_llm: LLMEnum = Field(
                default="default:default",
                title="Default LLM",
            )
            default_embedder: EmbedderEnum = Field(
                default="default:default",
                title="Default Embedder",
            )

        return DynamicSettings
