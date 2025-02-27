import httpx
import random
import aiofiles

from cat.log import log


def get_registry_url():
    return "https://registry.cheshirecat.ai"


async def registry_search_plugins(
    query: str = None,
    # author: str = None,
    # tag: str = None,
):
    registry_url = get_registry_url()

    try:
        if query:
            # search plugins
            url = f"{registry_url}/search"
            payload = {"query": query}

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)

            # check the connection's status
            if response.status_code == 200:
                return response.json()
            else:
                log.error(
                    f"Error with registry response: {response.status_code} {response.text}"
                )
                return []
        else:
            # list plugins as sorted by registry (no search)
            url = f"{registry_url}/plugins"
            params = {
                "page": 1,
                "page_size": 1000,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)

            # check the connection's status
            if response.status_code == 200:
                # TODO: registry should pluginssort by score,
                #  until then we sort here at random
                registry_plugins = response.json()["plugins"]
                random.shuffle(registry_plugins)
                return registry_plugins
            else:
                log.error(
                    f"Error with registry response: {response.status_code} {response.text}"
                )
                return []

    except Exception:
        log.error("Error with registry")
        return []


async def registry_download_plugin(url: str):
    log.info(f"Downloading {url}")

    registry_url = get_registry_url()
    payload = {"url": url}

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{registry_url}/download", json=payload)
        response.raise_for_status()

        plugin_zip_path = f"/tmp/{url.split('/')[-1]}.zip"

        async with aiofiles.open(plugin_zip_path, "wb") as f:
            await f.write(response.content)  # Write the content asynchronously

    log.info(f"Saved plugin as {plugin_zip_path}")
    return plugin_zip_path
