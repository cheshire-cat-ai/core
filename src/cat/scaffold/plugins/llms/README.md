# Language Models Pack

Named presets for the most common LLM vendors. Each one is a thin subclass of
core's `OpenAICompatibleProvider` that only sets a known `base_url`, so you just
pick a provider and drop in an API key.

One file per provider under `providers/`:

One file per provider under `providers/`:

| Preset       | File                      | Endpoint                                                   | Env var          |
| ------------ | ------------------------- | ---------------------------------------------------------- | ---------------- |
| `openai`     | `providers/openai.py`     | `https://api.openai.com/v1`                                | `OPENAI_KEY`     |
| `anthropic`  | `providers/anthropic.py`  | `https://api.anthropic.com/v1/`                            | `ANTHROPIC_KEY`  |
| `gemini`     | `providers/gemini.py`     | `https://generativelanguage.googleapis.com/v1beta/openai/` | `GEMINI_KEY`     |
| `openrouter` | `providers/openrouter.py` | `https://openrouter.ai/api/v1`                             | `OPENROUTER_KEY` |
| `ollama`     | `providers/ollama.py`     | `http://localhost:11434/v1`                                | `OLLAMA_URL`     |
| `vllm`       | `providers/vllm.py`       | `http://localhost:8000/v1`                                 | `VLLM_URL`       |

All presets speak the OpenAI wire format and inherit message/tool conversion,
streaming, and embedding from the core engine — this plugin adds **no extra
Python dependencies**.

## Configuring via environment

Every preset reads its defaults from the env var above — API keys for cloud
vendors, the server URL for local Ollama/vLLM. Set one and the provider works out
of the box: the settings page asks every provider for its live model list, so a
configured one shows up in the `default_llm` / `default_embedder` dropdown
**without any manual save**. An unconfigured provider just reports no models (no
key → no call), so nothing is dialed that can't answer.

## Using a preset

Set `default_llm` / `default_embedder` to a `provider:model` string, e.g.
`openai:gpt-4o`, `anthropic:claude-sonnet-4-6`, or `ollama:llama3.2`, and fill in
the provider's API key in its settings.

## Adding a vendor

Need another OpenAI-compatible endpoint? Drop a new file in `providers/` with a
subclass of `OpenAICompatibleProvider` setting its `slug` and `base_url` — the
plugin loader auto-discovers it. Need a native, non-OpenAI wire format? Author it
as its own plugin extending `cat.services.model_providers.base.ModelProvider`.
