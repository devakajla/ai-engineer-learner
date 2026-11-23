---
title: Dictionaries
summary: A dict stores values under names (keys). Learn to read safely with get, change, loop, merge, count and group.
plan_ids: []
---

A **dictionary** (`dict`) stores **values** under **keys**, like a real dictionary stores a meaning under a word. It is how Python holds a record (a user, a settings file, a JSON object) and how you look something up by name. A dict keeps the **order** in which you added the keys.

## Create and read

Write `key: value` pairs inside curly braces:

```python
user = {"name": "Dev", "age": 25}
user["name"]        # -> 'Dev'
user["email"]       # KeyError: 'email'    this key does not exist
len(user)           # -> 2
```

Keys must be **hashable**: strings, numbers and tuples (of those) are fine, but a list is not. Values can be anything.

## Read safely with `get`

`d[key]` raises an error when the key is missing. `d.get(key)` does not:

```python
user.get("email")              # -> None        no error
user.get("email", "unknown")   # -> 'unknown'   your own default value
```

To check if a key exists, use `in`. Note that `in` checks the **keys**, not the values:

```python
"name" in user      # -> True
"Dev" in user       # -> False   "Dev" is a value, not a key
```

## Add, change and delete

```python
user["email"] = "dev@example.com"   # add a new key
user["age"] = 26                    # change a value
del user["email"]                   # delete a key (KeyError if it is missing)
age = user.pop("age")               # remove a key and give back its value -> 26
user.pop("zzz", None)               # no error if the key is missing
```

## Loop over a dict

```python
prices = {"apple": 3, "pear": 5}

for key in prices:                  # the keys
    print(key)
# -> apple
# -> pear

for value in prices.values():       # the values
    print(value)
# -> 3
# -> 5

for key, value in prices.items():   # both, as (key, value) pairs
    print(key, value)
# -> apple 3
# -> pear 5
```

`.items()` gives `(key, value)` tuples. You unpack them in the `for` line (lesson 9). If you need a plain list, wrap it: `list(prices.keys())`.

## Update and merge

`update` copies the pairs of one dict into another. If a key already exists, the new value wins.

```python
a = {"x": 1, "y": 2}
b = {"y": 99, "z": 3}

a.update(b)            # changes a
print(a)               # -> {'x': 1, 'y': 99, 'z': 3}

c = {"x": 1} | {"x": 5, "y": 2}   # the | sign makes a NEW dict
print(c)               # -> {'x': 5, 'y': 2}    the right dict wins
```

## Counting things

A very common job is to count how many times each thing appears. Here is how, step by step, for the letters of `"banana"`:

1. Start with an empty dict.
2. For each letter, read its count with `get(letter, 0)`. If we have not seen it, the count is `0`.
3. Add 1 and store it back.

```python
text = "banana"
counts = {}
for ch in text:
    counts[ch] = counts.get(ch, 0) + 1
print(counts)   # -> {'b': 1, 'a': 3, 'n': 2}
```

The same idea works for words:

```python
words = "the cat and the dog".split()
counts = {}
for w in words:
    counts[w] = counts.get(w, 0) + 1
print(counts)   # -> {'the': 2, 'cat': 1, 'and': 1, 'dog': 1}
```

## Swapping keys and values

Loop over `items()` and store each pair the other way round:

```python
d = {"a": 1, "b": 2}
flipped = {}
for key, value in d.items():
    flipped[value] = key
print(flipped)   # -> {1: 'a', 2: 'b'}
```

## Grouping with `setdefault`

Sometimes each key must hold a **list** of items. `setdefault(key, default)` gives back the value if the key exists. If the key is missing, it stores `default` and gives that back. Because of this, you can write one line that works the first time and every other time:

```python
words = ["apple", "avocado", "banana"]
by_letter = {}
for w in words:
    by_letter.setdefault(w[0], []).append(w)
print(by_letter)   # -> {'a': ['apple', 'avocado'], 'b': ['banana']}
```

Read the line like this: "get the list for this first letter (or start an empty one), then append the word to it."

## Dicts inside dicts

Real data often has dicts and lists inside each other, like JSON:

```python
order = {
    "id": 1,
    "customer": {"name": "Ada", "city": "London"},
    "items": [{"sku": "A1", "qty": 2}, {"sku": "B2", "qty": 1}],
}
order["customer"]["city"]       # -> 'London'
order["items"][0]["qty"]        # -> 2
```

## Copying

```python
a = {"x": 1}
b = a            # the same dict with two names
c = a.copy()     # a new dict (a shallow copy, like for lists)
```

## A little deeper (optional)

- `keys()`, `values()` and `items()` are **views**. They show the dict as it is now, and they change when the dict changes.
- `d.get("k", [])` only **returns** the default. It does not store it in the dict. `setdefault` stores it.
- The `collections` module has `Counter` and `defaultdict` that do counting and grouping for you. You will meet imports in lesson 14.

## Common mistakes

- Using `d[key]` for a key that may be missing. Use `d.get(key)` or check with `in`.
- Thinking `x in d` checks the values. It checks the keys.
- Adding or deleting keys while looping over the same dict. This is a `RuntimeError`. Loop over `list(d)`, or build a new dict.
- Using a list as a key: `TypeError: unhashable type: 'list'`. Use a tuple instead.

## Summary

- A dict maps unique keys to values and keeps the order you added them.
- `d[k]` raises `KeyError` when the key is missing. `d.get(k, default)` does not.
- Loop with `.keys()`, `.values()` and `.items()`. Merge with `.update()` or `|`. The right-hand value wins.
- Count with `d[k] = d.get(k, 0) + 1`. Group with `setdefault(k, []).append(x)`.
- Dicts and lists inside each other can describe JSON-like data.
