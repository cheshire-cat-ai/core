from cat.env import get_env

from cat.utils import singleton


@singleton
class CacheManager:
    def __init__(self):
        cache_type = get_env("CCAT_CACHE_TYPE")
        if cache_type == "file_system":
            cache_dir = get_env("CCAT_CACHE_DIR")
            from cat.cache.file_system_cache import FileSystemCache
            self.cache = FileSystemCache(cache_dir)
        else:
            from cat.cache.in_memory_cache import InMemoryCache
            self.cache = InMemoryCache()
