import time


class CacheItem:
    
    def __init__(self, key, value, ttl=None):
        self.key = key
        self.value = value
        self.ttl = ttl
        self.created_at = time.time()

    def is_expired(self):
        if self.ttl == -1 or self.ttl is None:
            return False

        return (self.created_at + self.ttl) < time.time()

    def __repr__(self):
        return f'CacheItem(key={self.key}, value={self.value}, ttl={self.ttl}, created_at={self.created_at})'
