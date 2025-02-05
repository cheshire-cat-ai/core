from cat.cache.base_cache import BaseCache
from cat.cache.cache_item import CacheItem

from cat.utils import singleton


@singleton
class InMemoryCache(BaseCache):
    """Cache implementation using a python dictionary.

    Attributes
    ----------
    cache : dict
        Dictionary to store the cache.

    """

    def __init__(self):
        self.cache = {}

    def insert(self, cache_item):
        """Insert a key-value pair in the cache.

        Parameters
        ----------
        cache_item : CacheItem
            Cache item to store.

        """
        self.cache[cache_item.key] = cache_item

    def get_item(self, key) -> CacheItem:
        """Get the value stored in the cache.

        Parameters
        ----------
        key : str
            Key to retrieve the value.

        Returns
        -------
        any
            Value stored in the cache.

        """
        item = self.cache.get(key)

        if item and item.is_expired():
            del self.cache[key]
            return None

        return item

    def get_value(self, key):
        """Get the value stored in the cache.

        Parameters
        ----------
        key : str
            Key to retrieve the value.

        Returns
        -------
        any
            Value stored in the cache.

        """


        item = self.get_item(key)
        if item:
            return item.value
        return None

    def delete(self, key):
        """Delete a key-value pair from the cache.

        Parameters
        ----------
        key : str
            Key to delete the value.

        """
        if key in self.cache:
            del self.cache[key]