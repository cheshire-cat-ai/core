"""
Single source of configuration defaults for the Cheshire Cat.

These are plain UPPERCASE module constants and this file is the reference for
every available setting. To override any of them, create a `config.py` in your
project folder and redefine the constant there.

That `config.py` is plain Python, so you can read `.env` / `os.environ` yourself
if you want.
"""

# Public address the Cat is reachable at (protocol, host, port).
# Must be set in production so the Cat is aware of its own address.
URL = "http://localhost:1865"

# Database connection. Supports sqlite and postgresql.
# e.g. "postgresql://user:password@localhost/dbname"
SQL = "sqlite:///data/core/core.db"

# Master API key. Auth is always on: out of the box the key is the well-known
# dev value "meow" (matching the default JWT secret below), so a fresh project
# works immediately but is never silently wide open. Change it for production.
# Setting it to None disables key auth entirely (JWT-only; no open gate).
API_KEY = "meow"

# JWT signing secret and token lifetime (in minutes).
JWT_SECRET = "meow_jwt"
JWT_EXPIRE_MINUTES = 60 * 24  # 1 day

# Self-reload during development (turn off in production).
DEBUG = True

# Log level: DEBUG | INFO | WARNING | ERROR | CRITICAL
LOG_LEVEL = "INFO"

# Uvicorn/FastAPI operating behind an https proxy.
HTTPS_PROXY_MODE = False
# Comma separated list of IPs to trust with proxy headers ("*" trusts all).
CORS_FORWARDED_ALLOW_IPS = "*"

# CORS.
CORS_ENABLED = True
# Comma separated list of allowed origins, or "*" to allow all.
CORS_ALLOWED_ORIGINS = "*"

# Default LLM and embedder, as a "provider:model" string (e.g. "openai:gpt-4o",
# "ollama:llama3.2"). "default:default" is the keyless built-in fallback — a fresh
# install answers with a clear "configure me" message instead of crashing.
# CoreSettings starts from these; the settings page can override and persist them.
DEFAULT_LLM = "default:default"
DEFAULT_EMBEDDER = "default:default"

# Anonymous telemetry.
TELEMETRY = True
