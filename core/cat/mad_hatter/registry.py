import requests

from cat.log import log


async def registry_search_plugins(
    query: str = None,
    #author: str = None,
    #tag: str = None,
):
    
    registry_url = "https://registry.cheshirecat.ai"

    try:
        if query:
            # search plugins
            url = f"{registry_url}/search"
            payload = {
                "query": query
            }
            response = requests.post(url, json=payload)
            return response.json()
        else:
            # list plugins as sorted by registry (no search)
            url = f"{registry_url}/plugins"
            params = {
                "page": 1,
                "page_size": 1000,
            }
            response = requests.get(url, params=params)
            return response.json()["plugins"]
        
    except Exception as e:
        log(e, "ERROR")
        return []
