# Fix the mutable default

This function has the classic bug:

```python
def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags
```

Rewrite `add_tag(tag, tags=None)` so that:

- with no `tags`, each call starts from a **fresh** list
- when the caller passes a list, the tag is appended to **that** list (same object) and it is returned

```python
add_tag("a")          # -> ["a"]
add_tag("b")          # -> ["b"]       (not ["a", "b"])
mine = ["x"]
add_tag("y", mine)    # -> ["x", "y"], and mine is now ["x", "y"]
```
