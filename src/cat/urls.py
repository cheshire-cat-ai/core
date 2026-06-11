
from cat.env import get_env
from urllib.parse import urljoin

API_PREFIX = "/api/v2"

BASE_URL = get_env("CCAT_URL")
API_URL = urljoin(BASE_URL, f"{API_PREFIX.strip('/')}/")

# TODOV2: method join(sub_path) to get full url from base instead of urljoin every time