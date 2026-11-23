---
title: Modules & imports
summary: Split your code into files, use code from other files and from Python's standard library, and learn what packages and __name__ are.
plan_ids: []
---

A **module** is just a Python file. A **package** is a folder of modules. With `import` you can use code from another file instead of copying it. Python also comes with a huge toolbox of ready-made modules called the **standard library**, so you do not have to write everything yourself.

## `import`

```python
import math
print(math.sqrt(16))    # -> 4.0
print(math.pi)          # -> 3.141592653589793
```

`import math` gives you the module `math`. You use its tools with a dot: `math.sqrt`, `math.pi`.

There are a few styles:

```python
from math import sqrt, pi     # bring in only these names
print(sqrt(25))               # -> 5.0     no "math." needed

import datetime as dt         # "as" gives a shorter name
print(dt.date(2025, 1, 31))   # -> 2025-01-31
```

- `import x` keeps `x.` in front of the names, so it is always clear where a name comes from.
- `from x import y` brings in only `y`.
- `as` gives the module a shorter or clearer name.
- Do not write `from math import *`. It brings in every name and makes the code hard to follow.

Put all imports at the **top** of the file. A common order is: the standard library first, then other people's packages, then your own files. Leave a blank line between the groups.

## A few useful standard modules

A step-by-step example with `math`. How long is the edge around a circle of radius 3?

1. Import the module: `import math`.
2. Use `math.pi` for the number pi.
3. Write the formula: `2 * math.pi * 3`.

```python
import math
print(2 * math.pi * 3)    # -> 18.84955592153876
```

More modules:

```python
import math
math.floor(2.7)         # -> 2     round down
math.ceil(2.1)          # -> 3     round up

import random
random.randint(1, 6)    # a random whole number from 1 to 6

import json
json.dumps({"a": 1})    # -> '{"a": 1}'
```

### `Counter`: count things

`Counter` (from the `collections` module) counts how often each item appears. It works like a dict, so `.items()`, `.values()` and `in` all work.

```python
from collections import Counter

counts = Counter("banana")
print(counts)                   # -> Counter({'a': 3, 'n': 2, 'b': 1})
counts["a"]                     # -> 3
counts.most_common(1)           # -> [('a', 3)]   the most common (item, count)
list(counts.values())           # -> [1, 3, 2]
```

It does the same job as the counting loop you wrote in the dictionaries lesson, in one line.

### Dates

```python
from datetime import date

start = date.fromisoformat("2025-01-01")    # text "YYYY-MM-DD" to a date
end = date(2025, 3, 1)
gap = end - start
print(gap)         # -> 59 days, 0:00:00
print(gap.days)    # -> 59
```

Subtracting two dates gives a `timedelta`. Its `.days` is the number of days as an `int`.

## Your own modules

Say you have two files in the same folder:

```python
# utils.py
def double(n):
    return n * 2
```

```python
# main.py
import utils
from utils import double

print(utils.double(4))   # -> 8
print(double(5))         # -> 10
```

Python finds `utils` because the folder of the file you run is searched for imports.

> Do not name your own file like a standard module (`random.py`, `json.py`, `math.py`). Your file would hide the real one.

## `if __name__ == "__main__":`

Every module has a built-in name called `__name__`.

- When you **run** a file directly, its `__name__` is `"__main__"`.
- When another file **imports** it, `__name__` is the module's own name.

So you can write a file that works as a library and also as a program:

```python
# tools.py
def add(a, b):
    return a + b

if __name__ == "__main__":
    print(add(2, 3))     # runs only for: python tools.py
```

Importing `tools` from another file does **not** print anything.

## A little deeper (optional)

**Packages.** A folder of modules is a package. A file named `__init__.py` (it can be empty) marks the folder:

```
shop/
    __init__.py
    cart.py
    pricing.py
main.py
```

```python
from shop.cart import add_item
from shop import pricing
```

Inside a package you can also use relative imports: `from .pricing import total` (the `.` means "this package").

**How Python finds a module.** It looks in this order: built-in modules, the folder of your script, then installed packages (`sys.path`). The first match wins. A module is loaded only once and then remembered, so importing it again is cheap.

**Third-party packages.** Packages from PyPI (like `requests` or `fastapi`) are installed with a tool such as `uv add requests`, usually into a virtual environment (lesson 1). Then you `import requests` like any other module.

**Circular imports.** If `a.py` imports `b.py` and `b.py` imports `a.py`, you can get an `ImportError`. Fix it by moving the shared code into a third module, or by importing inside the function that needs it.

## Common mistakes

- Using `from module import *`. You cannot see where names come from.
- Naming your file like a standard module (`math.py`, `random.py`).
- Running work at import time (like `print` or a network call at the top of a file). Put it in a function or under `if __name__ == "__main__":`.
- `ModuleNotFoundError`: the wrong folder, a package that is not installed, or the virtual environment is not active.
- Circular imports.

## Summary

- A module is a `.py` file. A package is a folder of modules.
- `import x`, `from x import y` and `import x as z`. Keep imports at the top.
- `math`, `random`, `collections`, `datetime` and `json` are very useful standard modules.
- `Counter` counts items. `date.fromisoformat` reads a date from text, and subtracting two dates gives `.days`.
- `if __name__ == "__main__":` runs code only when the file is run directly.
- Avoid `import *`, avoid names of standard modules, and avoid circular imports.
