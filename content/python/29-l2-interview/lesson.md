---
title: Level 2 interview questions
summary: The Level 2 topics as interviewers ask them, with follow-up questions, short model answers, and tools for the three coding exercises.
plan_ids: [PY-01, PY-02, PY-03, PY-04, PY-05, PY-06, PY-07]
---

This module is practice for interviews. How to use it:

1. Read a question and **answer it out loud first** (or type it to Claude and ask for feedback).
2. Then read the model answer.

Interviewers rarely stop after the first answer. They ask 2 or 3 follow-up questions to see how deep you understand. The follow-ups below are the usual ones.

## 1. Names, values and mutability (lesson 18)

**Q: What is printed, and why?**

```python
def add(item, bucket=[]):
    bucket.append(item)
    return bucket

add(1)
print(add(2))
```

**A:** `[1, 2]`. A default value is made **once**, when the function is defined. Every call that uses the default shares the same list. The fix: use `bucket=None`, and make a new list inside the function.

Another one:

```python
a = [[0] * 2] * 2
a[0][0] = 9
print(a)     # -> [[9, 0], [9, 0]]
```

The outer list holds the **same** inner list twice. Changing one changes both. The fix: `[[0] * 2 for _ in range(2)]`.

Follow-ups:

- *Is Python "pass by reference"?* It is **pass by object reference**. The function gets a reference to the same object. Changing the object (mutating) is seen by the caller. Pointing the name at a new object (rebinding) is not.
- *Shallow copy or deep copy?* A shallow copy copies only the outer container, and the inner objects are shared. `copy.deepcopy` copies everything inside, too.
- *Why can a list not be a dict key?* A key's hash must never change. A list can change, so it is not hashable.

## 2. Classes and OOP (lessons 19 and 20)

**Q: When do you use a dataclass, a Pydantic model or a plain class?**

**A:** A **dataclass** for data inside your own code (it writes `__init__`, `__repr__` and `__eq__`, but does not check types). A **Pydantic model** where data comes in from outside and must be checked (API requests, config, AI output). A **plain class** when behaviour matters more than data (services, repositories).

What is printed?

```python
class A:
    items = []

x, y = A(), A()
x.items.append(1)
y.items = [2]
print(A.items, x.items, y.items)    # -> [1] [1] [2]
```

`items` is a **class** attribute, shared by all objects. `append` changes the shared list. But `y.items = [2]` makes a new attribute on `y` only.

Follow-ups:

- *You write `__eq__`. What else must you think about?* `__hash__`. If you define `__eq__` only, Python sets `__hash__` to `None`, and the object is unhashable. Make an object hashable only if it does not change. (A `dataclass(frozen=True)` is hashable.)
- *Composition or inheritance?* Composition is "has a". Inheritance is "is a". A `TaskService` is not a kind of repository, it **uses** one. If you pass the repository in, you can swap it (memory to SQL) and pass a fake one in tests.
- *ABC or Protocol?* An ABC is enforced when you create the object. A Protocol only describes the shape, and a type checker checks it.

## 3. Iterators and generators (lesson 22)

**Q: How would you count errors per service in a 20 GB log file?**

**A:** Stream it. A file is a lazy iterator, so loop over it line by line. Use a generator to parse each line and filter the errors. Add each one to a `Counter`. The memory use stays small, whatever the file size.

What is printed?

```python
def gen():
    yield 1
    yield 2

g = gen()
print(list(g), list(g))     # -> [1, 2] []
```

A generator can be used only once.

Follow-ups:

- *Iterable or iterator?* An iterable gives an iterator with `iter()`. An iterator gives items with `next()`, raises `StopIteration` at the end, and is used up after one pass.
- *What if the loop stops early?* The generator is closed, and its `finally` and `with` blocks still run.
- *Where do generators appear in FastAPI?* In `StreamingResponse` (streaming AI answers) and in `yield` dependencies.

## 4. Closures and decorators (lesson 23)

**Q: Write a decorator that retries a function when it raises `ConnectionError`, up to N times.**

**A:** It needs three levels: `retry(attempts)` returns `decorator(func)`, which returns `wrapper(*args, **kwargs)`. The wrapper loops, catches **only** the temporary error, waits longer each time, raises the error again after the last try, and uses `functools.wraps(func)`.

What is printed?

```python
from functools import lru_cache

calls = 0

@lru_cache
def sq(x):
    global calls
    calls += 1
    return x * x

sq(3); sq(3); sq(4)
print(calls)    # -> 2
```

`sq(3)` is worked out once and then remembered. `sq(4)` is a new argument.

Follow-ups:

- *Why `functools.wraps`?* It keeps the name and docstring. Logs and frameworks need them.
- *What is a closure?* An inner function that remembers the variables of its outer function. Use `nonlocal` to change one.
- *What is wrong with `[lambda: i for i in range(3)]`?* Late binding. All the lambdas see the final `i`. Fix it with a default argument: `lambda i=i: i`.

## 5. Context managers and errors (lessons 21 and 24)

**Q: Design a helper that runs database work inside a transaction.**

**A:** A context manager. Begin when it starts, hand out the connection, commit if the block succeeds, and **roll back and raise the error again** if it fails.

What is printed?

```python
try:
    print("a")
    raise ValueError
except ValueError:
    print("b")
else:
    print("c")
finally:
    print("d")
# -> a
# -> b
# -> d
```

`else` runs only if there was **no** error. `finally` always runs.

Follow-ups:

- *What if `__exit__` returns `True`?* The error is hidden. It is dangerous unless you meant it.
- *What does `raise X from e` do?* It keeps the first error as `__cause__`, so the traceback shows the root cause.
- *How do you design your own error classes?* One base `AppError`, with child classes for each case that carry data (like `NotFoundError(resource, id)`). Turn them into HTTP status codes at the edge of the app, not deep inside.

## 6. Type hints and Pydantic (lessons 27 and 28)

**Q: Are type hints enforced at runtime? Then how does FastAPI use them?**

**A:** Python does **not** enforce them. A type checker (mypy, pyright) checks them before running. FastAPI reads the hints while running, to find where each parameter comes from, to check and convert data with Pydantic, and to build the API docs.

Another one. An update model has only optional fields, and the client sends `{"title": null}`. Which call gives `{"title": None}`? `model_dump(exclude_unset=True)`. `exclude_none=True` would drop the field.

Follow-ups:

- *`Any` or `object`?* `Any` switches checking off. `object` makes you check the type first.
- *How do you check two fields together in Pydantic?* A `@model_validator(mode="after")`.
- *Why is Pydantic v2 fast?* Its core is written in Rust. `model_validate_json` reads and checks in one pass.

## 7. Quick answers

| Question | Short answer |
|---|---|
| `is` or `==` | `is` checks identity, `==` checks equality. Use `is` only for `None`. |
| `@classmethod` or `@staticmethod` | a classmethod gets `cls` (good for alternative constructors). A staticmethod gets nothing. |
| `__repr__` or `__str__` | `__repr__` is for developers and is exact. `__str__` is for users. |
| What does `lru_cache` need? | a pure function and hashable arguments |
| Naive or aware datetime | an aware one has a time zone. Always store UTC aware times. |
| `deque` or `list` for a queue | `deque` pops from the left in O(1). A list takes O(n). |
| `groupby` trap | the input must be sorted by the same key |
| EAFP or LBYL | try and handle the error, or check first. Python prefers EAFP. |

## Tools for the three coding exercises

These small examples show the tools. They are not the answers.

### A cache that forgets the oldest (exercise 1)

`collections.OrderedDict` is a dict that **remembers the order** of its keys. Two methods matter:

```python
from collections import OrderedDict

d = OrderedDict()
d["a"] = 1
d["b"] = 2
d["c"] = 3

d.move_to_end("a")                 # move key "a" to the end (the newest)
print(list(d))                     # -> ['b', 'c', 'a']

oldest = d.popitem(last=False)     # remove from the front (the oldest)
print(oldest)                      # -> ('b', 2)
print(list(d))                     # -> ['c', 'a']
```

Think about it: which end is the "least recently used" one? When should a key be moved? When do you remove one? To say the complexity out loud: both of these are O(1).

For the interview discussion, you could also build it from a dict and a doubly linked list. The dict finds a node in O(1), and the list moves a node to the front in O(1).

### A clock you can control (exercise 2)

Code that uses the real time is hard to test. A trick: **pass the clock in** as a parameter. In a test, pass a fake clock.

```python
import time

def make_timer(clock=time.monotonic):
    start = clock()
    def elapsed():
        return clock() - start
    return elapsed

now = [0.0]                          # a list, so the lambda below can see changes
timer = make_timer(clock=lambda: now[0])
now[0] = 7.5
print(timer())                       # -> 7.5
```

To remember results by their arguments, you need a **key** that is hashable. A tuple of the arguments works: `key = args`. The keyword arguments are a dict, which is not hashable, so you turn them into a tuple, too. Think about what `sorted(kwargs.items())` gives you.

The cache can be a plain dict that holds `(time_saved, value)` for each key. The value is old when `now - time_saved >= seconds`.

### Recursion and `setdefault` (exercise 3)

**Recursion** means a function that calls itself for a smaller part of the problem. Here it goes through lists inside lists. A generator can `yield from` itself:

```python
def numbers(data):
    for item in data:
        if isinstance(item, list):
            yield from numbers(item)      # go deeper
        else:
            yield item                    # a plain value

print(list(numbers([1, [2, [3, 4]], 5])))     # -> [1, 2, 3, 4, 5]
```

The plan has two cases: "a container, so go inside" and "a plain value, so give it out". For `flatten`, the container is a `dict` (`isinstance(value, dict)`), and the pieces of the key are joined with the separator as you go down.

`dict.setdefault(key, default)` returns the value for `key`. If the key is missing, it first stores `default` and then returns it:

```python
groups = {}
groups.setdefault("a", []).append(1)
groups.setdefault("a", []).append(2)
print(groups)      # -> {'a': [1, 2]}
```

For `unflatten`, split each key with `key.split(sep)`, walk down the pieces, and use `setdefault` to create a nested dict when it is missing. Think about what should happen if a piece you want to go into is **not** a dict (that is the conflict case).

## How to practise

1. Do the three coding exercises **under time pressure** (20 to 25 minutes each), like a real interview.
2. Say the complexity out loud **before** you run the tests.
3. Ask Claude: *"Act as an interviewer. Ask me 5 follow-up questions on decorators, one at a time, and grade my answers."*

## Summary

- Know the traps: shared default lists, `[[0] * 2] * 2`, class attributes shared by all objects, and used-up generators.
- Know the pairs: `else` and `finally`, `is` and `==`, ABC and Protocol, `exclude_none` and `exclude_unset`.
- Say the reason, not only the answer: why does it happen, and how do you fix it?
- For the coding exercises, name the tool first (`OrderedDict`, an injected clock, recursion), then write the code.
