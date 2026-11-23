---
title: "Dictionaries"
summary: "Dicts for counting, grouping and fast lookup, with get, items and setdefault."
plan_ids: []
---

A dictionary maps **keys** to **values**. Lookup by key is fast. It is the most useful tool for counting, grouping and "have I seen this and what was it?".

## Create, read, write

```python
ages = {"asha": 30, "dev": 28}
print(ages["dev"])        # -> 28
ages["ravi"] = 25         # add
ages["dev"] = 29          # update
del ages["asha"]          # remove
print(ages)               # -> {'dev': 29, 'ravi': 25}
print("dev" in ages)      # -> True    (checks keys)
```

`ages["zoe"]` raises `KeyError` when the key is missing.

## `get` with a default

```python
print(ages.get("zoe"))        # -> None
print(ages.get("zoe", 0))     # -> 0
```

## Loop over a dict

```python
d = {"a": 1, "b": 2}
for k in d:
    print(k)            # -> a, b
for k, v in d.items():
    print(k, v)         # -> a 1, b 2
print(list(d.keys()))   # -> ['a', 'b']
print(list(d.values())) # -> [1, 2]
```

## Pattern: counting

```python
def count_items(items):
    counts = {}
    for x in items:
        counts[x] = counts.get(x, 0) + 1
    return counts

print(count_items(["a", "b", "a"]))   # -> {'a': 2, 'b': 1}
```

> Memorise `counts[x] = counts.get(x, 0) + 1`. It appears in a huge number of problems.

## Pattern: grouping

```python
def group_by_first_letter(words):
    groups = {}
    for w in words:
        key = w[0]
        if key not in groups:
            groups[key] = []
        groups[key].append(w)
    return groups

print(group_by_first_letter(["apple", "avocado", "bean"]))
# -> {'a': ['apple', 'avocado'], 'b': ['bean']}
```

`setdefault` does the same in one line:

```python
groups = {}
groups.setdefault("a", []).append("apple")
print(groups)   # -> {'a': ['apple']}
```

## Pattern: remember what you saw

Store a value you may need later, keyed by something you will look up:

```python
def two_sum(nums, target):
    seen = {}                    # value -> index
    for i, n in enumerate(nums):
        need = target - n
        if need in seen:
            return [seen[need], i]
        seen[n] = i
    return None

print(two_sum([2, 7, 11, 15], 9))   # -> [0, 1]
```

## Order

Dicts keep the order in which keys were added.

## Common mistakes

- `KeyError`: reading a missing key. Use `get` or check `in`.
- Changing a dict while looping over it.
- Expecting `in` to look at values: it checks keys.
- Using a list as a key (unhashable). Use a tuple.

## Summary

- `d[k]`, `d[k] = v`, `get`, `in`, `del`, `items`, `keys`, `values`.
- Counting: `counts[x] = counts.get(x, 0) + 1`.
- Grouping: list per key, with `setdefault` or an `if`.
- Remember-what-I-saw: store value to index in a dict.
- Reference: `reference/dicts.md`.
