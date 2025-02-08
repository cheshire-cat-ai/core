import os

from cat.cache.cache_manager import CacheManager
from cat.cache.in_memory_cache import InMemoryCache
from cat.cache.file_system_cache import FileSystemCache


def test_cache_type():

    chaches = [
        ("file_system", FileSystemCache),
        ("in_memory", InMemoryCache),
    ]

    for cache_type, cache_class in chaches:

        os.environ["CCAT_CACHE_TYPE"] = cache_type
        cache_manager = CacheManager()
        
        assert cache_manager.cache_type == cache_type
        assert isinstance(cache_manager.cache, cache_class)
        
        # clean up env
        del os.environ["CCAT_CACHE_TYPE"]

