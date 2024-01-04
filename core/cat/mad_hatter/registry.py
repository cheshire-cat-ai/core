import requests

from cat.log import log


def get_registry_url():
    return "https://registry.cheshirecat.ai"


async def registry_search_plugins(
    query: str = None,
    #author: str = None,
    #tag: str = None,
):
    
    registry_url = get_registry_url()

    try:
        if query:
            # search plugins
            url = f"{registry_url}/search"
            payload = {
                "query": query
            }
            response = requests.post(url, json=payload)
            
            # check the connection's status
            if response.status_code == 200:
                return response.json()
            else:
                log.error(f"Error with registry response {response.status_code}: {response.text}")
                return []
        else:
            # list plugins as sorted by registry (no search)
            url = f"{registry_url}/plugins"
            params = {
                "page": 1,
                "page_size": 1000,
            }
            response = requests.get(url, params=params)
            
            # check the connection's status
            if response.status_code == 200:
                return response.json()["plugins"]
            else:
                log.error(f"Error with registry response {response.status_code}: {response.text}")
                return []
            
        
    except Exception as e:
        log.error(e)
        return []
    

def registry_download_plugin(url: str) -> str:

    log.info(f"Downloading {url}")

    registry_url = get_registry_url()
    payload = {
        "url": url
    }
    response = requests.post(f"{registry_url}/download", json=payload)
    plugin_zip_path = f"/tmp/{url.split('/')[-1]}.zip"
    with open(plugin_zip_path, "wb") as f:
        f.write(response.content)

    log.info(f"Saved plugin as {plugin_zip_path}")

    return plugin_zip_path
