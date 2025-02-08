import os
import pytest

from cat.cache.cache_item import CacheItem
from cat.cache.in_memory_cache import InMemoryCache
from cat.cache.file_system_cache import FileSystemCache


# utility to create cache instances
def create_cache(cache_type):
    if cache_type == "in_memory":
        return InMemoryCache()
    elif cache_type == "file_system":
        return FileSystemCache("/tmp_cache")
    else:
        assert False


@pytest.mark.parametrize("cache_type", ["in_memory", "file_system"])
def test_cache_creation(cache_type):

    cache = create_cache(cache_type)
    
    if cache_type == "in_memory":
        assert cache.items == {}
        assert cache.max_items == 100
    else:
        assert cache.cache_dir == "/tmp_cache"
        assert os.path.exists("/tmp_cache")
        assert os.listdir("/tmp_cache") == []


@pytest.mark.parametrize("cache_type", ["in_memory", "file_system"])
def test_cache_get_insert(cache_type):

    cache = create_cache(cache_type)

    assert cache.get_item("a") is None
    
    c1 = CacheItem("a", [])  
    cache.insert(c1)
    assert cache.get_item("a").value == []
    assert cache.get_value("a") == []

        
    c1.value = [0]
    cache.insert(c1) # will be overwritten
    assert cache.get_item("a").value == [0]
    assert cache.get_value("a") == [0]


    c2 = CacheItem("b", {})
    cache.insert(c2)
    assert cache.get_item("a").value == [0]
    assert cache.get_value("a") == [0]
    assert cache.get_item("b").value == {}
    assert cache.get_value("b") == {}


@pytest.mark.parametrize("cache_type", ["in_memory", "file_system"])
def test_cache_delete(cache_type):

    cache = create_cache(cache_type)

    c1 = CacheItem("a", [])
    cache.insert(c1)
    
    cache.delete("a")
    assert cache.get_item("a") is None


# only in_memory cache
def test_cache_max_items():

    cache = InMemoryCache()

    for i in range(cache.max_items + 2):
        cache.insert(CacheItem(str(i), i))
        assert len(cache.items) <= cache.max_items

    assert len(cache.items) == cache.max_items // 10 * 9 + 2
    cached_values = [c.value for c in cache.items.values()]
    assert cached_values == list(range(10, cache.max_items + 2))




