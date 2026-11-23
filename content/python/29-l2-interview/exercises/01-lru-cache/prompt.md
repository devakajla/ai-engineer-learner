# Implement an LRU cache

A classic interview problem. Write `LRUCache(capacity)`:

- `get(key)` → value, or `-1` if missing. Accessing a key makes it **most recently used**.
- `put(key, value)` → insert/update; updating also makes it most recently used. If the cache exceeds `capacity`, evict the **least recently used** key.
- Both operations **O(1)**.
- `__len__` returns the number of items.

```python
c = LRUCache(2)
c.put(1, "a"); c.put(2, "b")
c.get(1)          # -> "a"   (1 is now most recent)
c.put(3, "c")     # evicts 2
c.get(2)          # -> -1
```

Hint: `collections.OrderedDict` has `move_to_end()` and `popitem(last=False)`. (Bonus discussion for the interview: how would you build it from a dict + doubly linked list?)
