---
title: Stdlib essentials
summary: Four standard-library tools used in almost every backend - collections, datetime with time zones, json and logging.
plan_ids: [PY-07]
---

Python comes with a big **standard library**: modules that are already installed, ready to `import`. They save you from writing (and fixing) common code yourself. This lesson covers four that almost every backend uses: `collections`, `datetime`, `json` and `logging`.

## `collections`: better containers

You met `Counter` in lesson 14. Here are the useful ones together.

### `Counter`: count things

```python
from collections import Counter

c = Counter("mississippi")
print(c.most_common(2))        # -> [('i', 4), ('s', 4)]
print(c["z"])                  # -> 0      a missing key counts as 0
```

`most_common(n)` gives the `n` biggest counts as a list of `(item, count)` pairs. When two counts are equal, the one that appeared first comes first.

A step-by-step example: find the most common words in a sentence.

1. Make the text lowercase, so `The` and `the` count as one word.
2. Split it into words with `.split()`.
3. Give the list of words to `Counter`.
4. Ask for `most_common(n)`.

```python
text = "Red blue RED green red blue"
words = text.lower().split()
print(Counter(words).most_common(2))    # -> [('red', 3), ('blue', 2)]
```

### `defaultdict`: a dict that creates missing values

With a normal dict, `groups["a"].append(...)` fails if `"a"` is not there yet. A `defaultdict(list)` creates a new empty list for any missing key:

```python
from collections import defaultdict

groups = defaultdict(list)
for word in ["apple", "avocado", "banana"]:
    groups[word[0]].append(word)       # word[0] is the first letter

print(dict(groups))    # -> {'a': ['apple', 'avocado'], 'b': ['banana']}
```

`dict(groups)` turns it back into a plain dict. A string has a `split` method that can cut at a character: `"a@x.io".split("@", 1)` gives `['a', 'x.io']`. The `1` means "cut at most one time".

### `deque`: a fast queue with an optional size limit

A `deque` (say "deck") is a list that is fast at **both ends**. With `maxlen`, it keeps only the **last** N items and drops the oldest automatically:

```python
from collections import deque

recent = deque(maxlen=3)
for event in ["a", "b", "c", "d"]:
    recent.append(event)

print(list(recent))        # -> ['b', 'c', 'd']     "a" fell off
```

`list.pop(0)` is slow for a big list, because every item must move. `deque.popleft()` is fast. Use a `deque` for queues and for "the last N things".

A class can hold a `deque` inside it and give a simple interface:

```python
class LastThree:
    def __init__(self):
        self._items = deque(maxlen=3)

    def add(self, x):
        self._items.append(x)

    def items(self):
        return list(self._items)       # oldest first

box = LastThree()
for n in [1, 2, 3, 4]:
    box.add(n)
print(box.items())    # -> [2, 3, 4]
```

### `namedtuple`: a tiny record

```python
from collections import namedtuple

Point = namedtuple("Point", "x y")
p = Point(1, 2)
print(p.x, p.y)       # -> 1 2
```

It is a tuple whose items have names. It cannot be changed.

| You need | Use |
|---|---|
| to count things | `Counter` |
| to group things | `defaultdict(list)` |
| a queue, or "the last N" | `deque` (with `maxlen`) |
| a tiny record that cannot change | `namedtuple` (or a frozen dataclass) |

## `datetime`: dates and times

The most important rule for backends: **store and compute times in UTC, and use time-zone-aware objects. Change to a local time zone only to show it to a person.**

**UTC** is the world's standard time. **Time-zone-aware** means the object knows its zone. A **naive** datetime has no zone, so nobody knows what time it really means.

```python
from datetime import UTC, datetime, timedelta

now = datetime.now(UTC)          # aware: knows it is UTC
naive = datetime.now()           # naive: no zone. Avoid!
```

`datetime.now(UTC)` is the right way. `datetime.now()` and the old `datetime.utcnow()` both give naive objects.

> If you compare a naive datetime with an aware one (`<`, `>`), Python raises a `TypeError`. It refuses to guess.

### Reading and writing times as text

The standard text form is **ISO 8601**, for example `2026-11-20T18:00:00+05:30`. The `+05:30` at the end is the **offset** from UTC.

```python
dt = datetime.fromisoformat("2026-11-20T18:00:00+05:30")
print(dt.tzinfo is None)            # -> False    it is aware
print(dt.isoformat())               # -> 2026-11-20T18:00:00+05:30

utc = dt.astimezone(UTC)            # the same moment, in UTC
print(utc.isoformat())              # -> 2026-11-20T12:30:00+00:00
```

`dt.tzinfo` is `None` for a naive datetime. That is how you check. A text without an offset (like `2026-11-20T18:00:00`) gives a naive datetime.

`astimezone(...)` converts to another zone. It is still the **same moment**, just written in another zone.

### Showing a time in a local zone

Use `zoneinfo.ZoneInfo` with a zone name, and `strftime` with a format string. A few format codes: `%d` day, `%b` short month name, `%Y` year, `%I` hour (12-hour), `%M` minute, `%p` AM/PM.

```python
from zoneinfo import ZoneInfo

local = utc.astimezone(ZoneInfo("Asia/Kolkata"))
print(local.strftime("%d %b %Y, %I:%M %p"))     # -> 20 Nov 2026, 06:00 PM
```

### `timedelta`: a length of time

Subtracting two datetimes gives a `timedelta`. It has these parts:

- `.days`: whole days.
- `.seconds`: the seconds **left over after the days** (from 0 to 86399). It is not the total.
- `.total_seconds()`: the whole length in seconds.

```python
a = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)
b = datetime(2026, 11, 22, 17, 30, tzinfo=UTC)
left = b - a
print(left.days)                  # -> 2
print(left.seconds)               # -> 19800
print(left.seconds // 3600)       # -> 5       whole hours after the days
print(left.total_seconds())       # -> 192600.0
```

So "2 days and 5 hours" is `left.days` and `left.seconds // 3600`. You can add or subtract a timedelta: `a + timedelta(days=3, hours=2)`.

### A worked example: how long until a deadline?

1. Both times must be aware.
2. If `now` is not before `due`, the answer is `"overdue"`.
3. Otherwise subtract, and build the text from `.days` and `.seconds // 3600`.

```python
def time_left(due, now):
    if now >= due:
        return "overdue"
    left = due - now
    return f"{left.days}d {left.seconds // 3600}h"

print(time_left(b, a))    # -> 2d 5h
print(time_left(a, b))    # -> overdue
```

To **measure how long code takes**, use `time.perf_counter()` and not `datetime.now()`. The wall clock can jump (for example when it is corrected).

## `json`: text that many languages understand

JSON is the text format that APIs use. It looks like a Python dict or list.

```python
import json

text = json.dumps({"id": 1, "tags": ["a"]}, sort_keys=True)
print(text)                  # -> {"id": 1, "tags": ["a"]}
data = json.loads(text)      # text -> Python
print(data["id"])            # -> 1
```

`dumps` makes text (the `s` is for string). `loads` reads text. `json.dump` and `json.load` (no `s`) work with files. `sort_keys=True` puts the keys in order, so the same data always gives the same text.

JSON knows only dict, list, str, int, float, bool and `None`. Other types (like `datetime`, `Decimal` and `set`) raise a `TypeError`. To teach `json` about them, pass a function as `default=`. It is called for each value that JSON does not understand. It must return something JSON understands, or raise `TypeError`.

```python
from decimal import Decimal

def encode(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()          # a string
    if isinstance(obj, Decimal):
        return str(obj)                 # a string keeps money exact
    if isinstance(obj, set):
        return sorted(obj)              # a list in a fixed order
    raise TypeError(f"cannot encode {type(obj).__name__}")

row = {"at": datetime(2026, 1, 1, tzinfo=UTC), "price": Decimal("9.99"), "tags": {"b", "a"}}
print(json.dumps(row, sort_keys=True, default=encode))
# -> {"at": "2026-01-01T00:00:00+00:00", "price": "9.99", "tags": ["a", "b"]}
```

For money, use a string, not a `float`. A float can bring small rounding errors.

## `logging`: messages for the people who run your app

`print` is fine for learning. A real app uses `logging`, because log messages have **levels**, times and the name of the module, and you can decide where they go.

```python
import logging

logger = logging.getLogger(__name__)    # one logger per file, named after it

def import_rows(rows):
    for i, row in enumerate(rows):
        if "id" not in row:
            logger.warning("skipping row %s: missing id", i)
    logger.info("checked %d rows", len(rows))
```

Rules:

- Put the values as **extra arguments** (`"... %s", value`), not in an f-string. Python then builds the text only if that level is switched on, and log tools can group the messages that share the same template.
- Use `logger.exception("...")` inside an `except` block. It logs the message **and the full traceback**.
- Configure logging **once**, when the app starts:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
```

The levels, from the smallest:

| Level | Use it for |
|---|---|
| DEBUG | detailed information for developers (off in production) |
| INFO | normal events (a request was served) |
| WARNING | something odd, but handled (a bad row was skipped) |
| ERROR | an operation failed |
| CRITICAL | the app cannot continue |

Never log secrets, passwords or tokens.

## A little deeper (optional)

- **Structured logs.** In production, apps often log JSON, so tools (Datadog, Loki, CloudWatch) can search by field. You will see this in the FastAPI track.
- **Libraries and handlers.** A library should only create loggers. The application decides where the logs go.
- **Other modules worth knowing.** `uuid.uuid4()` makes random ids. `secrets.token_urlsafe()` makes tokens for password resets and logins. Never use `random` for anything about security, because it is predictable. Also: `hashlib`, `enum`, `heapq`, `bisect`, `re`, `subprocess`, `tempfile`.

## Common mistakes

- Using naive datetimes, `datetime.utcnow()`, or comparing naive with aware.
- Leaving `print` calls in production code.
- Using f-strings in log calls, or logging secrets.
- Using `random` for tokens instead of `secrets`.
- Using `list.pop(0)` for a queue instead of `deque.popleft()`.
- Reading `.seconds` of a `timedelta` as the total. Use `.total_seconds()`.

## Interview corner

- **Q: How do you handle time zones in a backend?** Store and compute in UTC with aware datetimes, send ISO 8601 with an offset, and convert to the user's zone only to show it.
- **Q: Why a `deque` and not a list for a queue?** A `deque` is fast at both ends. `list.pop(0)` must move every item.
- **Q: How do you turn a datetime or a Decimal into JSON?** Pass a `default=` function. Datetimes become ISO strings, and Decimals become strings.
- **Q: `print` or `logging`?** Logging has levels, formats, module names and one place to configure it.

## Summary

- `Counter` counts, `defaultdict(list)` groups, `deque(maxlen=...)` keeps the last N, `namedtuple` is a small record.
- Datetimes: aware and in UTC, ISO 8601 text, `zoneinfo` to show local time, `timedelta` for lengths of time (`.days`, `.seconds`, `.total_seconds()`).
- `json.dumps(..., default=...)` handles types JSON does not know.
- `logging.getLogger(__name__)`, configure once, `%s` arguments, `logger.exception` in `except` blocks, no secrets.
