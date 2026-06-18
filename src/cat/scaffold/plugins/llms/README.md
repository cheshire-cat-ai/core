# Language Models Pack

Named presets for the most common LLM vendors. Each one is a thin subclass of
core's `OpenAICompatibleProvider` that only sets a known `base_url`, so you just
pick a provider and drop in an API key.

| Preset      | Endpoint                                                      | Key needed |
| ----------- | ------------------------------------------------------------- | ---------- |
| `openai`    | `https://api.openai.com/v1`                                   | yes        |
| `anthropic` | `https://api.anthropic.com/v1/`                               | yes        |
| `gemini`    | `https://generativelanguage.googleapis.com/v1beta/openai/`    | yes        |
| `ollama`    | `http://localhost:11434/v1`                                   | no (local) |
| `vllm`      | `http://localhost:8000/v1`                                    | no (local) |

All presets speak the OpenAI wire format and inherit message/tool conversion,
streaming, and embedding from the core engine — this plugin adds **no extra
Python dependencies**.

## Using a preset

Set `default_llm` / `default_embedder` to a `provider:model` string, e.g.
`openai:gpt-4o`, `anthropic:claude-sonnet-4-6`, or `ollama:llama3.2`, and fill in
the provider's API key in its settings.

## Adding a vendor

Need another OpenAI-compatible endpoint? Add a subclass of
`OpenAICompatibleProvider` in `providers.py` with its `slug` and `base_url`.
Need a native, non-OpenAI wire format? Author it as its own plugin extending
`cat.services.model_providers.base.ModelProvider`.
