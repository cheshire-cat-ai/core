import time
from cat.cache.cache_item import CacheItem


def test_cache_item_creation():

    c = CacheItem("a", [])
    assert c.key == "a"
    assert c.value == []
    assert c.ttl is None

    c = CacheItem("b", {}, 10)
    assert c.key == "b"
    assert c.value == {}
    assert c.ttl == 10


def test_cache_item_expiration():

    c = CacheItem("a", {}, -1)
    assert not c.is_expired()

    c = CacheItem("a", {})
    assert not c.is_expired()

    c = CacheItem("a", {}, 1)
    assert not c.is_expired()
    time.sleep(1)
    assert c.is_expired()