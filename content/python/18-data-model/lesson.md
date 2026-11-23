---
title: "Data model: references & copies"
summary: How names, values and copies really work in Python. This is the root of many bugs in real programs.
plan_ids: [PY-01]
---

In Level 1 you learned that a variable is a name (a sticky note) stuck on a value. In this lesson we use that idea to explain the most common "weird" Python bugs. Almost all of them have the same cause: **two names pointing to one value that can change.**

## Names point to values

```python
a = [1, 2]
b = a              # no copy: b points to the SAME list
b.append(3)
print(a)           # -> [1, 2, 3]
print(a is b)      # -> True    "is" asks: the very same list?
```

Two different things can happen to a name, and they behave differently:

- **Changing** the value (mutating it) is seen through every name that points to it.
- **Pointing the name somewhere new** (rebinding it) affects only that one name.

```python
a = [1, 2]
b = a
b = b + [3]        # + builds a NEW list, and b now points to it
print(a)           # -> [1, 2]       a is unchanged
b += [4]           # for a list, += changes the list in place
```

> `x += y` **changes in place** for mutable values like lists, and **points x to a new value** for immutable values like numbers, strings and tuples. The syntax is the same, but the behavior is not.

## What happens to arguments in a function

When you call a function, the parameter name points to the **same value** the caller passed. Python calls this "pass by object reference".

```python
def add_item(items, item):
    items.append(item)       # changes the caller's list

def reset(items):
    items = []               # points the LOCAL name to a new list. The caller is not affected.

data = [1]
add_item(data, 2)
print(data)         # -> [1, 2]
reset(data)
print(data)         # -> [1, 2]    reset did nothing to data
```

The rule: a function can **change** a mutable argument, but it can **never make the caller's name point somewhere else**.

It is also polite for a function to **not** change its input when it does not need to. Build a new value instead. Here is a function that finds the duplicates in a list, and leaves the input alone:

```python
def find_duplicates(items):
    seen = set()
    duplicates = []
    for item in items:
        if item in seen:
            duplicates.append(item)
        seen.add(item)
    return duplicates

data = [3, 1, 3, 2, 1]
print(find_duplicates(data))   # -> [3, 1]
print(data)                    # -> [3, 1, 3, 2, 1]   unchanged
```

## The mutable default argument trap

You saw this in Level 1. A default value is made **once**, when the function is defined, not on every call:

```python
def add_tag(tag, tags=[]):      # ONE list, shared by every call
    tags.append(tag)
    return tags

add_tag("a")   # -> ['a']
add_tag("b")   # -> ['a', 'b']   surprise!
```

The fix is to use `None` as the default and make a fresh list inside:

```python
def add_tag(tag, tags=None):
    if tags is None:
        tags = []
    tags.append(tag)
    return tags
```

With this fix, a call without `tags` starts from a **new** list every time. A call with your own list adds to **your** list, and returns it.

This is one of the most asked Python interview questions.

## Shallow copy and deep copy

A **shallow copy** makes a new outer container, but the things inside are still shared. A **deep copy** copies everything inside as well.

```python
import copy

orig = {"tags": ["a", "b"], "n": 1}

s = orig.copy()            # a shallow copy
s["n"] = 2                 # the top level is separate, so orig["n"] is still 1
s["tags"].append("c")      # but the inner list is SHARED
print(orig["tags"])        # -> ['a', 'b', 'c']

d = copy.deepcopy(orig)    # a deep copy
d["tags"].append("z")
print(orig["tags"])        # -> ['a', 'b', 'c']    not affected
```

| Way | What is copied | Inner values |
|---|---|---|
| `b = a` | nothing | shared |
| `a.copy()`, `list(a)`, `a[:]`, `copy.copy(a)` | the outer container | **shared** |
| `copy.deepcopy(a)` | everything | separate |

Here is a step-by-step example. You have a base settings dict and you want a separate version for testing, without touching the base.

1. Make a deep copy of the base: `copy.deepcopy(BASE)`.
2. Change the copy, including values inside it.
3. The base stays the same.

```python
BASE = {"colors": ["red"], "size": {"w": 10}}

test = copy.deepcopy(BASE)
test["colors"].append("blue")
test["size"]["w"] = 99

print(BASE)    # -> {'colors': ['red'], 'size': {'w': 10}}   untouched
print(test)    # -> {'colors': ['red', 'blue'], 'size': {'w': 99}}
```

> Two copies made with `deepcopy` do not share anything with each other either.

### The list-of-lists trap

```python
grid = [[0] * 3] * 3       # three names for ONE inner list
grid[0][0] = 1
print(grid)                # -> [[1, 0, 0], [1, 0, 0], [1, 0, 0]]

grid = [[0] * 3 for _ in range(3)]   # three separate lists
grid[0][0] = 1
print(grid)                # -> [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
```

(`_` is a name that means "I do not need this value".)

## Same value or equal value?

- `is` asks: is it the very same value? (it compares `id()`)
- `==` asks: is the content equal? (it calls `__eq__`)

Small numbers and some strings are reused by Python, so `a is b` can be `True` for equal small values. Never depend on this. Use `==` to compare values, and use `is` only for `None`.

## Dunder methods: how your objects work with Python's syntax

A **dunder** method has a name with double underscores on both sides, like `__len__`. Python calls them behind the scenes when you use normal syntax:

| You write | Python calls |
|---|---|
| `len(x)` | `x.__len__()` |
| `x == y` | `x.__eq__(y)` |
| `x[k]` | `x.__getitem__(k)` |
| `print(x)` or `str(x)` | `x.__str__()` |
| `repr(x)` | `x.__repr__()` |
| `x + y` | `x.__add__(y)` |
| `for i in x` | `x.__iter__()` |

This idea is called the **data model**. It is why your own classes can behave like lists, numbers or dicts. You will write dunder methods in the next two lessons.

## A little deeper (optional)

**Hashing.** Values that can be dict keys or set members must be **hashable**: their hash number must never change. That is why a list (which can change) is not hashable.

**How Python frees memory.** CPython uses **reference counting**. Each value counts how many names point to it. When the count reaches 0, the value is freed at once. A **cyclic garbage collector** also cleans up values that point to each other in a circle (`a.ref = b` and `b.ref = a`). `del name` removes a *name*, not the value. `sys.getrefcount(value)` shows the count (one higher than you expect, because the call itself holds a reference).

## Common mistakes

- Using a mutable default argument.
- Thinking `b = a` or `a.copy()` gives you separate inner values.
- Building grids with `[[0] * n] * m`.
- Using `is` to compare numbers or strings.
- Changing a list while looping over it. Loop over a copy (`for x in items[:]`) or build a new list.

## Interview corner

- **Q: Is Python pass-by-value or pass-by-reference?** Neither exactly. It is "pass by object reference". The function gets a reference to the same value. Changing a mutable value is visible to the caller, but pointing the name at a new value is not.
- **Q: Why is `def f(x=[])` a bug?** The default list is made once, when the function is defined, and every call shares it. Use `None` and make the list inside.
- **Q: Shallow copy vs deep copy?** A shallow copy copies the outer container but shares the inner values. A deep copy copies everything.
- **Q: How does Python free memory?** With reference counting, plus a cyclic garbage collector for values that point to each other.

## Summary

- Names point to values. Assignment never copies.
- Changing a value is seen through every name. Pointing a name somewhere new affects only that name.
- Never use a mutable default argument. Use `None`.
- `.copy()` is shallow. `copy.deepcopy` is deep.
- Python syntax calls dunder methods. This is the data model.
