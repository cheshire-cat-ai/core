from typing import Type, Literal, TYPE_CHECKING

from pydantic import BaseModel, Field

from cat.db import DB
from cat.config.settings import settings as settings_manager
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
        # Static fallback schema (used by tooling that wants the bare shape).
        # The live UI schema is built by `settings_schema()` below, which turns
        # these into dropdowns of every model the installed providers expose.
        default_llm: str = Field(
            "default:default",
            title="Default LLM",
            description="provider:model (e.g. openai:gpt-4o, ollama:llama3.2).",
        )
        default_embedder: str = Field(
            "default:default",
            title="Default Embedder",
            description="provider:model (e.g. openai:text-embedding-3-small).",
        )

    @classmethod
    async def settings_schema(cls, app: "CheshireCat") -> Type[BaseModel]:
        """
        Dynamic schema: enumerate the LLMs/embedders every registered provider
        exposes, so the UI renders a dropdown instead of a free-text box.

        Robust by construction:
        - `default:default` is always first, so a fresh, keyless install still
          has a valid option ("nothing configured yet").
        - only providers the user has actually configured (a saved settings
          blob exists) are probed for their live model list. Opening the
          settings page must never storm every provider's default endpoint —
          a local vLLM/Ollama that isn't running, an OpenAI base_url with no
          key, etc. An untouched provider contributes nothing until configured.
        - the currently-saved values are always included, so changing one
          setting never resets another to default just because a provider's
          live list is momentarily empty (e.g. key removed).
        - a provider that errors or returns nothing is simply skipped.
        """

        llm_options = ["default:default"]
        embedder_options = ["default:default"]

        for slug, ProviderClass in app.registry.classes.get("model_providers", {}).items():
            if slug == "default":
                continue  # already seeded above

            # Skip providers the user has never configured, so we only ever dial
            # endpoints the user explicitly opted into.
            saved = await DB.load(settings_manager.key(ProviderClass))
            if not isinstance(saved, dict):
                continue

            try:
                provider = await app.get("model_providers", slug)
                llm_options += [f"{slug}:{m}" for m in await provider.list_llms()]
                embedder_options += [f"{slug}:{m}" for m in await provider.list_embedders()]
            except Exception as e:
                log.error(f"Error querying model provider {slug}: {e}")

        # Keep whatever is saved valid even if it is not in the live lists.
        # Read the raw blob directly — calling settings_manager.load() here would
        # recurse back into settings_schema().
        raw = await DB.load(settings_manager.key(cls))
        if isinstance(raw, dict):
            if raw.get("default_llm"):
                llm_options.append(raw["default_llm"])
            if raw.get("default_embedder"):
                embedder_options.append(raw["default_embedder"])

        # Dedup while preserving order.
        llm_options = list(dict.fromkeys(llm_options))
        embedder_options = list(dict.fromkeys(embedder_options))

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
