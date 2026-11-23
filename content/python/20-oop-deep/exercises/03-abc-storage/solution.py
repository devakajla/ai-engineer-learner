from abc import ABC, abstractmethod
from collections.abc import Callable


class KeyValueStore(ABC):
    @abstractmethod
    def get(self, key: str) -> str | None: ...

    @abstractmethod
    def set(self, key: str, value: str) -> None: ...

    @abstractmethod
    def delete(self, key: str) -> bool: ...


class MemoryStore(KeyValueStore):
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def delete(self, key: str) -> bool:
        return self._data.pop(key, None) is not None


class Cache:
    def __init__(self, store: KeyValueStore) -> None:
        self.store = store

    def get_or_set(self, key: str, compute: Callable[[], str]) -> str:
        value = self.store.get(key)
        if value is None:
            value = compute()
            self.store.set(key, value)
        return value
