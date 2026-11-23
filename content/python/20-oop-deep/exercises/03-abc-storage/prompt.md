# A storage contract with an ABC

1. Write an abstract base class `KeyValueStore(ABC)` with abstract methods `get(key) -> str | None`, `set(key, value) -> None`, `delete(key) -> bool`.
2. Implement `MemoryStore(KeyValueStore)` backed by a dict.
3. Write `Cache` that uses **composition**: `Cache(store: KeyValueStore)` with `get_or_set(key, compute)` — return the stored value if present, otherwise call `compute()`, store the result and return it.

```python
KeyValueStore()                 # TypeError (abstract)
cache = Cache(MemoryStore())
cache.get_or_set("a", lambda: "1")   # computes -> "1"
cache.get_or_set("a", lambda: "2")   # cached   -> "1"
```

`Cache` must work with **any** `KeyValueStore` implementation (the tests pass their own).
