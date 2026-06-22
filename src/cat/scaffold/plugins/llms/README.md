# Language Models Pack

Ready-made presets for the most common LLM vendors. Pick a provider, drop in an
API key, and go — every preset speaks the OpenAI wire format and adds **no extra
Python dependencies**.

| Preset       | Endpoint                                                   | Env var                    |
| ------------ | ---------------------------------------------------------- | -------------------------- |
| `openai`     | `https://api.openai.com/v1`                                | `OPENAI_KEY`               |
| `anthropic`  | `https://api.anthropic.com/v1/`                            | `ANTHROPIC_KEY`            |
| `gemini`     | `https://generativelanguage.googleapis.com/v1beta/openai/` | `GEMINI_KEY`               |
| `openrouter` | `https://openrouter.ai/api/v1`                             | `OPENROUTER_KEY`           |
| `ollama`     | `http://localhost:11434/v1`                                | `OLLAMA_URL`, `OLLAMA_KEY` |
| `vllm`       | `http://localhost:8000/v1`                                 | `VLLM_URL`, `VLLM_KEY`     |

## 1. Configure a provider

Go to UI settings page and insert your key/url.  
Otherwise it can be configured directly via `.env`:

```bash
export OPENAI_KEY=sk-...
```

## 2. Preselect a default llm / embedder at first launch

Pick which model the Cat should default to by setting `DEFAULT_LLM` /
`DEFAULT_EMBEDDER` to a `provider:model` string in your project `config.py`:

```python
# config.py
DEFAULT_LLM = "openai:gpt-4o"
DEFAULT_EMBEDDER = "openai:text-embedding-3-small"
```

Combined with the env var above, the Cat boots fully configured.

