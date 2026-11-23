# Dictionaries

Map **keys** to **values**. Lookup by key is fast. Keeps insertion order. Keys must be hashable.

| Tool | Does |
| --- | --- |
| `d[k]` | read (KeyError if missing) |
| `d[k] = v` | add or update |
| `d.get(k, default)` | safe read |
| `k in d` | key test |
| `del d[k]` / `d.pop(k)` | remove |
| `d.items()` `d.keys()` `d.values()` | views for looping |
| `d.setdefault(k, default)` | get or insert default |
| `dict(d)` | shallow copy |

## Read safely
```python
d = {"a": 1}
print(d.get("b"), d.get("b", 0))   # -> None 0
print("a" in d)                     # -> True
```
**Gotcha:** `in` checks keys, not values.

## Loop
```python
for k, v in {"a": 1, "b": 2}.items():
    print(k, v)   # -> a 1 / b 2
```
**Gotcha:** do not add or remove keys while looping.

## Counting
```python
counts = {}
for ch in "aab":
    counts[ch] = counts.get(ch, 0) + 1
print(counts)   # -> {'a': 2, 'b': 1}
```

## Grouping
```python
groups = {}
for w in ["hi", "yo", "hey"]:
    groups.setdefault(len(w), []).append(w)
print(groups)   # -> {2: ['hi', 'yo'], 3: ['hey']}
```
**Theory:** `setdefault` returns the existing value, or inserts the default and returns it.

## Remember what you saw
```python
seen = {}
for i, n in enumerate([2, 7]):
    seen[n] = i
print(seen)   # -> {2: 0, 7: 1}
```
This is the heart of two-sum: look up `target - n` in the dict. Lesson: `dsa/10-dicts`.
