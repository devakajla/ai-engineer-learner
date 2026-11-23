---
title: "OOP deep: dunders, dataclasses, ABCs"
summary: Make your classes work with Python syntax, write less code with dataclasses, define contracts with ABCs, and prefer composition.
plan_ids: [PY-06, SD-01]
---

In the last lesson you built classes. This lesson shows four tools that you will use again and again in real code:

- **Dunder methods**: make your objects work with `==`, `+`, `sorted()` and more.
- **Dataclasses**: write data classes with much less code.
- **ABCs**: define a contract that other classes must follow.
- **Composition**: build big things from small parts, instead of inheriting.

## Dunder methods: objects that feel built-in

Remember from lesson 18: Python calls methods with double underscores (`__eq__`, `__add__`) when you use normal syntax. If you write them in your class, your objects work with that syntax too.

A step-by-step example. A `Point` has `x` and `y`. We want to print it nicely, compare two points, add them, and sort them.

1. `__repr__` gives a clear text for the point.
2. `__eq__` says when two points are equal.
3. `__hash__` lets points go in sets and dicts. It must match `__eq__`.
4. `__add__` makes `p + q` work.
5. `__lt__` ("less than") makes `sorted()`, `min()` and `max()` work.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)

print(Point(1, 2) + Point(3, 4))               # -> Point(4, 6)
print(Point(1, 2) == Point(1, 2))              # -> True
print({Point(1, 2), Point(1, 2)})              # -> {Point(1, 2)}
print(sorted([Point(3, 0), Point(1, 5)]))      # -> [Point(1, 5), Point(3, 0)]
```

Rules to remember:

- If you define `__eq__` but not `__hash__`, Python makes your objects **unhashable** (they cannot go in a set or be a dict key). Equal objects must have equal hashes.
- For a type you do not support, return `NotImplemented` (not `False`). Python then tries the other side, and finally falls back to "not equal". So `Point(1, 2) == 5` is simply `False`.
- Only make an object hashable if it should not change.
- Methods can raise errors too. For example, `__add__` could raise a `ValueError` for objects that do not fit together.

More dunders: `__len__` (for `len(x)`), `__getitem__` (for `x[i]`), `__contains__` (for `in`) and `__bool__` (for truthiness: `if x:`).

```python
class Basket:
    def __init__(self, items):
        self.items = items

    def __len__(self):
        return len(self.items)

    def __bool__(self):
        return len(self.items) > 0

b = Basket(["a", "b"])
print(len(b), bool(b))                 # -> 2 True
print(bool(Basket([])))                # -> False
```

## Dataclasses: classes for data, with less code

For a class that mostly holds data, `__init__`, `__repr__` and `__eq__` are always the same boring code. `@dataclass` writes them for you. You list the **fields**, with a **type annotation** (`name: type`) after each name. (Lesson 27 teaches type hints. Here the annotation just says "this is a field".)

```python
from dataclasses import dataclass, field

@dataclass
class Book:
    title: str
    pages: int = 100                              # a default value
    tags: list = field(default_factory=list)      # a mutable default, done right
    read: bool = False

b = Book("Dune")
print(b)    # -> Book(title='Dune', pages=100, tags=[], read=False)
```

A dataclass does **not** allow `tags: list = []`. That would share one list between all objects. Use `field(default_factory=list)` and each object gets its own new list.

Useful options go in the brackets: `@dataclass(frozen=True)`.

| Option | What it does |
|---|---|
| `frozen=True` | objects cannot be changed (assigning raises an error), and they become hashable |
| `order=True` | adds `<`, `<=`, `>`, `>=`, comparing the fields in the order they are written |
| `slots=True` | uses less memory and is a little faster |
| `kw_only=True` | all fields must be given by name |

A dataclass does **not** check types while the program runs. `Book(title=5)` is accepted.

### `__post_init__`: checks after creation

`__post_init__` runs right after the generated `__init__`. Use it to check or clean values:

```python
@dataclass
class Book:
    title: str
    pages: int = 100

    def __post_init__(self):
        self.title = self.title.strip()           # clean the title
        if not self.title:
            raise ValueError("title is required")
        if self.pages <= 0:
            raise ValueError("pages must be positive")

print(Book("  Dune  ").title)    # -> Dune
```

### Sorting by a different field first

With `order=True`, objects are compared field by field, **in the order the fields are written**. If you want to sort by `pages` first but `title` is the first field, add a hidden first field that you fill in `__post_init__`:

```python
@dataclass(order=True)
class Book:
    sort_key: tuple = field(init=False, repr=False)   # hidden: not in __init__ or repr
    title: str
    pages: int = 100

    def __post_init__(self):
        self.sort_key = (self.pages, self.title)

books = [Book("B", 300), Book("A", 300), Book("Z", 50)]
print([b.title for b in sorted(books)])    # -> ['Z', 'A', 'B']
```

### A frozen dataclass

```python
@dataclass(frozen=True)
class BookId:
    value: int

a = BookId(1)
a.value = 2           # FrozenInstanceError: cannot assign to field
print({a, BookId(1)})   # -> {BookId(value=1)}   hashable, so it works in a set
```

**Dataclass or Pydantic?** A dataclass is a plain, fast container with no checks of types. Pydantic (lesson 28) **checks and converts** data. A good rule: use Pydantic where data enters your program (API requests, settings), and dataclasses inside your own code.

## Abstract base classes: a contract

An **abstract base class** (ABC) says "every class of this kind **must** have these methods". The methods are marked `@abstractmethod`.

```python
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def save(self, key, value):
        ...

    @abstractmethod
    def load(self, key):
        ...

class MemoryStorage(Storage):
    def __init__(self):
        self.data = {}

    def save(self, key, value):
        self.data[key] = value

    def load(self, key):
        return self.data.get(key)

Storage()             # TypeError: Can't instantiate abstract class Storage
s = MemoryStorage()
s.save("a", 1)
print(s.load("a"))    # -> 1
```

You cannot create an ABC itself. A child class that forgets an abstract method **fails when you create it**, not later in production.

## Composition over inheritance

- **Inheritance** means "is a": a `Dog` is an `Animal`.
- **Composition** means "has a": a `Car` has an `Engine`.

For many jobs, "has a" is the better design. A `Cache` is not a kind of storage. It **uses** a storage. So we pass the storage in:

```python
class Cache:
    def __init__(self, storage):         # the storage is given from outside
        self.storage = storage

    def get_or_make(self, key, make):
        value = self.storage.load(key)
        if value is None:
            value = make()               # make is a function that builds the value
            self.storage.save(key, value)
        return value

cache = Cache(MemoryStorage())
print(cache.get_or_make("a", lambda: "first"))     # -> first
print(cache.get_or_make("a", lambda: "second"))    # -> first   (it was saved)
```

(`lambda: "first"` is a tiny function with no name. You will learn lambdas in lesson 25. Here it just means "a function that gives back `first`".)

Because `Cache` only calls `load` and `save`, it works with **any** storage that follows the contract: memory, a file, a database, or a fake one for tests. This is a big reason to prefer composition.

Use inheritance for real "is a" cases and shallow trees: custom errors, and classes that implement an ABC.

## A little deeper (optional)

**Protocols.** A `Protocol` says "anything that has these methods fits", with **no inheritance needed**. Type checkers like mypy check it. ABCs enforce the contract when you create an object. Protocols describe the shape for type checking.

```python
from typing import Protocol

class CanLoad(Protocol):
    def load(self, key): ...
```

**Multiple inheritance and the MRO.** A class can have several parents. Python looks for a method in the **MRO** (method resolution order), shown by `ClassName.__mro__`. `super()` follows this order, not just "the one parent". Most of the time you meet this with **mixins**: small classes that add one skill.

**SOLID.** Five design ideas: Single responsibility (one reason to change per class), Open/closed (add new classes instead of editing old ones), Liskov substitution (a child must work wherever the parent works), Interface segregation (small contracts) and Dependency inversion (depend on contracts, and pass real parts in).

## Common mistakes

- Defining `__eq__` and then wondering why the object is unhashable.
- Writing `tags: list = []` in a dataclass. It raises `ValueError`. Use `field(default_factory=list)`.
- Deep inheritance trees only to reuse code. Prefer composition.
- Making changeable objects hashable. Their hash can change, and dict entries get lost.

## Interview corner

- **Q: If you write `__eq__`, what else must you think about?** `__hash__`. Equal objects need equal hashes, and Python sets `__hash__` to `None` if you only write `__eq__`.
- **Q: Dataclass, Pydantic model or NamedTuple?** A dataclass writes the boring methods and has no checks. Pydantic checks and converts data. A NamedTuple is a tuple with names that cannot change.
- **Q: ABC or Protocol?** An ABC needs inheritance and is enforced when you create the object. A Protocol only needs the right methods and is checked by type checkers.
- **Q: Composition or inheritance?** Composition is "has a" and is more flexible and easier to test. Inheritance is "is a".

## Summary

- Dunder methods plug your objects into Python syntax. `__eq__` needs a matching `__hash__`. Return `NotImplemented` for types you do not support.
- `@dataclass` writes the boring methods. Use `frozen`, `order`, `field(default_factory=...)` and `__post_init__`.
- ABCs define contracts that are enforced. Protocols describe a shape.
- Prefer composition: pass the parts in from outside.
