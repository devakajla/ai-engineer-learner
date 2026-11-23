from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
