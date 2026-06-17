from typing import Type, Literal
from pydantic import BaseModel, Field

from cat.services.service import SingletonService
from cat import log


class CoreSettings(SingletonService):
    """Framework-wide installation settings (default LLM, embedder, etc.)."""

    service_type = "config"
    slug = "core"
    name = "Core Settings"
    description = "Framework-wide installation defaults."

    class Settings(BaseModel):
        default_llm: str = "default:default"
        default_embedder: str = "default:default"

    async def settings_model(self) -> Type[BaseModel]:
        """Build a dynamic settings model with enum options from all model providers."""

        llm_options = ["default:default"]
        embedder_options = ["default:default"]

        for slug in self.ccat.factory.class_index.get("model_providers", {}):
            try:
                provider = await self.ccat.get("model_providers", slug)
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
