import asyncio
from typing import Type, Literal

from pydantic import BaseModel, Field

from cat.db import store
from cat.ambient.runtime import ccat
from cat.services.service import Service
from cat import log, config


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
            config.DEFAULT_LLM,
            title="Default LLM",
            description="provider:model (e.g. openai:gpt-4o, ollama:llama3.2).",
        )
        default_embedder: str = Field(
            config.DEFAULT_EMBEDDER,
            title="Default Embedder",
            description="provider:model (e.g. openai:text-embedding-3-small).",
        )

    @classmethod
    async def settings_schema(cls) -> Type[BaseModel]:
        """
        Dynamic schema: enumerate the LLMs/embedders every registered provider
        exposes, so the UI renders a dropdown instead of a free-text box.

        Robust by construction:
        - the keyless built-in fallback is always offered: the `default` provider
          lists its own model, so a fresh, keyless install always has a valid
          option ("nothing configured yet").
        - every registered provider is asked for its live model list, no gating
          here: whether a provider can answer is the provider's own call. An
          unconfigured one returns `[]` for free (no key → no client → no call),
          and a configured-but-unreachable one fails fast on its own discovery
          timeout. All providers are queried concurrently, so the page waits at
          most one discovery timeout, not one per provider.
        - the configured default (`config.DEFAULT_LLM`) and the currently-saved
          values are always included, so the default stays valid even when its
          provider is momentarily unreachable, and changing one setting never
          resets another.
        - a provider that errors or returns nothing simply contributes nothing.
        """

        # Seed with the configured default so it stays a valid option even if its
        # provider is unreachable when the page loads. The keyless fallback is
        # contributed by the `default` provider during discovery below.
        llm_options = [config.DEFAULT_LLM]
        embedder_options = [config.DEFAULT_EMBEDDER]

        async def discover(slug: str) -> "tuple[str, list[str], list[str]]":
            """Ask one provider for its models; never raise — return ([],[]) on failure."""
            try:
                provider = await ccat().get("model_providers", slug)
                return slug, await provider.list_llms(), await provider.list_embedders()
            except Exception as e:
                log.error(f"Error querying model provider {slug}: {e}")
                return slug, [], []

        slugs = list(ccat().registry.classes.get("model_providers", {}))
        for slug, llms, embedders in await asyncio.gather(*(discover(s) for s in slugs)):
            llm_options += [f"{slug}:{m}" for m in llms]
            embedder_options += [f"{slug}:{m}" for m in embedders]

        # Keep whatever is saved valid even if it is not in the live lists.
        # Read the raw blob directly — calling load_settings() here would
        # recurse back into settings_schema().
        raw = await store.load(cls._settings_key())
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
                default=config.DEFAULT_LLM,
                title="Default LLM",
            )
            default_embedder: EmbedderEnum = Field(
                default=config.DEFAULT_EMBEDDER,
                title="Default Embedder",
            )

        return DynamicSettings
