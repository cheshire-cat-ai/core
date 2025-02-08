from cat.env import get_env


class CacheManager:
    """Class to instantiate different cache types."""

    def __init__(self):

        self.cache_type = get_env("CCAT_CACHE_TYPE")
        
        if self.cache_type == "in_memory":
            from cat.cache.in_memory_cache import InMemoryCache
            self.cache = InMemoryCache()
        elif self.cache_type == "file_system":
            cache_dir = get_env("CCAT_CACHE_DIR")
            from cat.cache.file_system_cache import FileSystemCache
            self.cache = FileSystemCache(cache_dir)
        else:
            raise ValueError(f"Cache type {self.cache_type} not supported")