# Quick Reference

Open this page any time you forget a method. Each line says what it does, with a short example. For the reasoning behind each one, see the chapter in brackets.

**How to read:** `s` is a string, `L` a list, `d` a dict, `st` a set. A method that says *returns new* leaves the original unchanged. A method that says *in place* changes the object and returns `None`.

## The guide: what is in this booklet

| Ch | Topic | You will be able to |
| --- | --- | --- |
| 1 | Setup, first program | run code, read an error |
| 2 | Variables, numbers, strings | store data, format text, slice |
| 3 | Conditions and loops | decide and repeat |
| 4 | Lists, tuples, sets, dicts | choose the right container |
| 5 | Functions | write reusable code |
| 6 | Files, modules, errors | read files, handle failures |
| 7 | Comprehensions, sorting | transform data briefly |
| 8 | Data model | understand names, copies, dunders |
| 9 | OOP | write classes and dataclasses |
| 10 | Iterators, generators | handle streams and big data |
| 11 | Closures, decorators | wrap and cache functions |
| 12 | Context managers | guarantee cleanup |
| 13 | Type hints, Pydantic | validate data |
| 14 | Concurrency | choose threads, processes, async |
| 15 | asyncio | run waiting jobs together |
| 16 | pytest, uv | test and package |
| 17 | Profiling | measure and speed up |
| 18 | Interview bank | rehearse answers |

**Suggested daily rhythm:** read one chapter (about 40 minutes), type every small example yourself, do the exercises, then check the answers at the end of the booklet.

## Strings (2)

| Call | Does | Example |
| --- | --- | --- |
| `s.strip()` | remove spaces at both ends (returns new) | `" a ".strip()` gives `"a"` |
| `s.lower()`, `s.upper()` | change case | `"Ab".lower()` gives `"ab"` |
| `s.title()`, `s.capitalize()` | Each Word, or First letter only | `"a b".title()` gives `"A B"` |
| `s.split(sep)` | cut into a list | `"a,b".split(",")` gives `["a","b"]` |
| `sep.join(list)` | glue a list into text | `"-".join(["a","b"])` gives `"a-b"` |
| `s.replace(a, b)` | replace all `a` by `b` | `"aa".replace("a","b")` gives `"bb"` |
| `s.find(x)` | position of `x`, or `-1` | `"abc".find("c")` gives `2` |
| `s.index(x)` | position, or error if missing | |
| `s.count(x)` | how many times | `"banana".count("a")` gives `3` |
| `s.startswith(x)`, `s.endswith(x)` | true or false | |
| `s.isdigit()`, `s.isalpha()` | check the kind of characters | `"12".isdigit()` gives `True` |
| `s.zfill(n)`, `s.center(n)`, `s.ljust(n)`, `s.rjust(n)` | pad to width `n` | `"x".zfill(3)` gives `"00x"` |
| `s.partition(sep)` | split into three parts | `"a-b".partition("-")` gives `("a","-","b")` |
| `s.removeprefix(x)` | drop a start | `"abc".removeprefix("a")` gives `"bc"` |
| `f"{x:.2f}"` | format: 2 decimals | `f"{3.14159:.2f}"` gives `3.14` |
| `f"{n:,}"` | thousands separator | `1,234,567` |

## Lists (4)

| Call | Does |
| --- | --- |
| `L.append(x)` | add at the end (in place) |
| `L.insert(i, x)` | add at position `i` (in place) |
| `L.extend(other)` | add all items of `other` (in place) |
| `L.pop()` / `L.pop(i)` | remove and **return** the last / the item at `i` |
| `L.remove(x)` | remove the first item equal to `x` |
| `L.index(x)`, `L.count(x)` | position, number of times |
| `L.sort(key=, reverse=)` | sort **in place**, returns `None` |
| `sorted(L)` | sorted **new** list |
| `L.reverse()` | reverse in place |
| `L.copy()` | shallow copy |
| `L[a:b]`, `L[::-1]` | slice, reversed copy |
| `x in L`, `len(L)` | membership, size |

## Tuples (4)

| Call | Does |
| --- | --- |
| `t = (1, 2)`, `(5,)` | create; one item needs a comma |
| `a, b = t` | unpack |
| `t.count(x)`, `t.index(x)` | the only two methods |

## Sets (4)

| Call | Does |
| --- | --- |
| `st.add(x)`, `st.discard(x)` | add, remove if present (no error) |
| `st.remove(x)` | remove, error if missing |
| `a & b`, `a - b`, `a ^ b` | both, only in a, in only one (and `a.union(b)` for everything) |
| `a.issubset(b)` | is every item of a in b? |
| `set()` | empty set (`{}` is a dict) |

The union operator is the pipe sign: `a | b` gives everything from both sets.

## Dicts (4)

| Call | Does |
| --- | --- |
| `d[k]`, `d[k] = v` | read (error if missing), write |
| `d.get(k, default)` | read safely |
| `d.setdefault(k, v)` | read, or set `v` if missing |
| `d.pop(k)`, `del d[k]` | remove |
| `d.update(other)` | merge |
| `d.keys()`, `d.values()`, `d.items()` | views to loop over |
| `k in d` | key exists? |
| `{k: v for ...}` | dict comprehension |
| `dict.fromkeys(items)` | keys from items, ordered and unique |

## Built-in functions

| Call | Does | Call | Does |
| --- | --- | --- | --- |
| `len(x)` | size | `sum(x)` | total |
| `min(x)`, `max(x)` | smallest, biggest (`key=`) | `abs(n)` | absolute value |
| `round(n, d)` | round to `d` places | `divmod(a, b)` | `(a // b, a % b)` |
| `sorted(x)` | new sorted list | `reversed(x)` | reverse iterator |
| `enumerate(x)` | `(index, item)` pairs | `zip(a, b)` | pairs side by side |
| `range(a, b, step)` | a sequence of numbers | `map(f, x)`, `filter(f, x)` | apply, keep |
| `any(x)`, `all(x)` | at least one, every | `isinstance(x, T)` | is it a kind of T? |
| `type(x)` | its type | `int()`, `float()`, `str()`, `bool()`, `list()` | convert |
| `input(text)` | read text from the user | `print(..., sep=, end=)` | show |
| `open(path, mode)` | open a file | `id(x)` | object identity |
| `getattr(o, "n")`, `hasattr(o, "n")` | attribute by name | `dir(o)` | list its attributes |

## `collections` (4, 8)

```python
from collections import Counter, defaultdict, deque, namedtuple

Counter("banana").most_common(2)   # -> [('a', 3), ('n', 2)]
d = defaultdict(list); d["a"].append(1)   # -> {'a': [1]}  (missing key starts as [])
q = deque([1, 2]); q.appendleft(0)        # fast at both ends
P = namedtuple("P", "x y"); P(1, 2).x     # -> 1
```

## `itertools` (10)

| Call | Result |
| --- | --- |
| `chain(a, b)` | `a` then `b` |
| `islice(it, n)` | the first `n` items |
| `count(5)` | 5, 6, 7... forever |
| `product("ab", [1, 2])` | `('a',1) ('a',2) ('b',1) ('b',2)` |
| `permutations([1,2,3], 2)` | ordered pairs |
| `combinations([1,2,3], 2)` | unordered pairs: `(1,2) (1,3) (2,3)` |
| `accumulate([1,2,3])` | running total: `1 3 6` |
| `groupby("aabbb")` | runs of equal items (sort first) |
| `zip_longest(a, b)` | zip that does not stop early |

## `pathlib` and `json` (6)

```python
from pathlib import Path
p = Path("data") / "a.txt"
p.write_text("hi"); p.read_text(); p.exists(); p.name; p.suffix; p.parent
p.mkdir(parents=True, exist_ok=True); list(Path(".").glob("*.py")); p.unlink()

import json
json.dumps(obj); json.loads(text)      # to / from text
json.dump(obj, fh); json.load(fh)      # to / from a file
```

## `datetime` (stdlib)

```python
from datetime import datetime, timedelta, date
dt = datetime(2026, 11, 22, 9, 30)
dt.strftime("%d %b %Y %H:%M")          # -> 22 Nov 2026 09:30
dt + timedelta(days=10)                # -> 2026-12-02 09:30:00
(date(2026, 12, 25) - date(2026, 11, 22)).days   # -> 33
datetime.strptime("2026-01-05", "%Y-%m-%d")      # text to datetime
dt.isoformat()                         # -> 2026-11-22T09:30:00
```

## `re`: regular expressions (text patterns)

| Pattern | Meaning |
| --- | --- |
| `\d`, `\w`, `\s` | a digit, a word character, a space |
| `.`, `*`, `+`, `?` | any char, 0 or more, 1 or more, optional |
| `{4}`, `[abc]`, `^`, `$` | exactly 4, one of these, start, end |
| `( )`, `(?P<name> )` | group, named group |

```python
import re
m = re.search(r"(\d+)-(\w+)", "id 42-abc x")
m.group(), m.group(1), m.groups()     # -> '42-abc', '42', ('42', 'abc')
re.findall(r"\d+", "a1 b22 c333")     # -> ['1', '22', '333']
re.sub(r"\s+", " ", "a   b \n c")     # -> 'a b c'
re.split(r",\s*", "a, b,c")           # -> ['a', 'b', 'c']
re.fullmatch(r"\w+@\w+\.com", "a@b.com")   # a match object, or None
```

## Patterns you will use daily

| Pattern | Shape | Ch |
| --- | --- | --- |
| accumulator | `total = 0` then `total += x` in a loop | 3 |
| counter dict | `d[k] = d.get(k, 0) + 1` | 4 |
| seen-set | `if x in seen: ... ; seen.add(x)` | 4 |
| safe default | `def f(x, items=None): if items is None: items = []` | 5 |
| read lines | `with open(p) as f: for line in f:` | 6 |
| transform | `[f(x) for x in xs if cond]` | 7 |
| sort by rule | `sorted(xs, key=lambda x: (-x.n, x.name))` | 7 |
| deep copy | `copy.deepcopy(x)` for nested data | 8 |
| lazy pipeline | chain generators | 10 |
| wrap a function | `@functools.wraps(fn)` inside a decorator | 11 |
| cleanup | `with` / `@contextmanager` | 12 |
| validate | `Model.model_validate(data)` | 13 |
| run waiting jobs together | `await asyncio.gather(...)` | 15 |
| limit parallel calls | `asyncio.Semaphore(n)` | 15 |
| test | `uv run pytest`, `parametrize`, fixtures | 16 |

## Commands

| Command | Does |
| --- | --- |
| `uv init name` | new project |
| `uv add pkg` / `uv add --dev pkg` | add a library |
| `uv run file.py` | run in the project |
| `uv run pytest -q` | run tests |
| `uv sync` | install what the lock file lists |
