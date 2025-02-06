
from abc import ABC, abstractmethod

class BaseCache(ABC):

    @abstractmethod
    def insert(self, cache_item):
        pass

    @abstractmethod
    def get_item(self, key):
        pass

    @abstractmethod
    def get_value(self, key):
        pass

    @abstractmethod
    def delete(self, key):
        pass


