
from cat.env import get_env
from urllib.parse import urljoin

BASE_URL = get_env("CCAT_URL")
API_URL = urljoin(BASE_URL, "api/v2/")

# TODOV2: method join(sub_path) to get full url from base instead of urljoin every time