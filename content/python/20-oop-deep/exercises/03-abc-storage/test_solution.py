import pytest

from solution import Cache, KeyValueStore, MemoryStore


def test_abstract():
    with pytest.raises(TypeError):
        KeyValueStore()

    class Incomplete(KeyValueStore):
        def get(self, key):
            return None

    with pytest.raises(TypeError):
        Incomplete()


def test_memory_store():
    s = MemoryStore()
    assert s.get("x") is None
    s.set("x", "1")
    assert s.get("x") == "1"
    assert s.delete("x") is True and s.delete("x") is False
    assert isinstance(s, KeyValueStore)


def test_cache_composition():
    calls = []

    def compute():
        calls.append(1)
        return "v"

    cache = Cache(MemoryStore())
    assert cache.get_or_set("a", compute) == "v"
    assert cache.get_or_set("a", compute) == "v"
    assert len(calls) == 1


def test_cache_with_other_store():
    class LoggingStore(MemoryStore):
        def __init__(self):
            super().__init__()
            self.sets = 0

        def set(self, key, value):
            self.sets += 1
            super().set(key, value)

    store = LoggingStore()
    Cache(store).get_or_set("k", lambda: "1")
    assert store.sets == 1, "Cache must use the store it was given"
