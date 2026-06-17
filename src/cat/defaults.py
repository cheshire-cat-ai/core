"""
Single source of configuration defaults for the Cheshire Cat.

These are plain UPPERCASE module constants and this file is the reference for
every available setting. To override any of them, create a `config.py` in your
project folder (the current working directory) and redefine the constant there.

That `config.py` is plain Python, so you can read `.env` / `os.environ` yourself
if you want — core never parses environment files on your behalf.
"""

# Public address the Cat is reachable at (protocol, host, port).
# Must be set in production so the Cat is aware of its own address.
URL = "http://localhost:1865"

# Database connection. Supports sqlite and postgresql.
# e.g. "postgresql://user:password@localhost/dbname"
SQL = "sqlite:///data/core/core.db"

# Protect endpoints with an API key. None means open (handy in development).
API_KEY = None

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

# Anonymous telemetry.
TELEMETRY = True
