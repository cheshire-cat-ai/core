from cat.cache.base_cache import BaseCache
from cat.cache.cache_item import CacheItem


class InMemoryCache(BaseCache):
    """Cache implementation using a python dictionary.

    Attributes
    ----------
    cache : dict
        Dictionary to store the cache.

    """

    def __init__(self):
        self.items = {}
        self.max_items = 100

    def insert(self, cache_item):
        """Insert a key-value pair in the cache.

        Parameters
        ----------
        cache_item : CacheItem
            Cache item to store.

        """

        # add new item
        self.items[cache_item.key] = cache_item
        
        # clean up cache if it's full
        if len(self.items) >= self.max_items:

            # sort caches by creation time
            sorted_items = sorted(
                self.items.items(),
                key=lambda x: x[1].created_at,
            )

            # delete 10% of the oldest items
            # not efficient, but it's honest work
            # TODO: index items also by creation date
            for k, v in sorted_items[:self.max_items//10]:
                self.delete(k)


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
        item = self.items.get(key)

        if item and item.is_expired():
            del self.items[key]
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
        if key in self.items:
            del self.items[key]
