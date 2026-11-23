---
title: Closures & decorators
summary: Functions as values, closures that remember data, and decorators, the idea behind @app.get, @lru_cache and retries.
plan_ids: [PY-03]
---

You will see lines like `@app.get("/tasks")`, `@lru_cache` and `@pytest.fixture` all over Python code. These are **decorators**. They are built from two simpler ideas: **functions are values** and **closures**. We will go through them one by one.

## Functions are values

In Python a function is a value, like a number or a string. You can store it in a name, put it in a dict, pass it to another function, and return it from a function.

```python
def shout(text):
    return text.upper()

f = shout                 # no brackets: f is now another name for the function
print(f("hi"))            # -> HI

handlers = {"shout": shout}
print(handlers["shout"]("x"))    # -> X
```

A function that takes a function, or gives one back, is called a **higher-order function**. You have used some already: `sorted(words, key=len)` takes a function.

## Scope: where Python looks for a name

When Python needs a name, it looks in four places, in this order (**LEGB**):

1. **L**ocal: inside the current function.
2. **E**nclosing: inside the functions around it.
3. **G**lobal: the top level of the file.
4. **B**uilt-in: names like `len` and `print`.

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        return x          # finds the x in the enclosing function
    return inner()

print(outer())    # -> enclosing
```

## Closures

You can write a function **inside** another function. A **closure** is an inner function that remembers the variables of the outer function, **even after the outer function has finished**.

```python
def make_multiplier(factor):
    def multiply(x):
        return x * factor        # factor is remembered
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5), triple(5))      # -> 10 15
```

`make_multiplier(2)` is finished, but `double` still remembers that `factor` is `2`.

### Changing a remembered value: `nonlocal`

An inner function can **read** an outer variable. To **change** it (assign to it), you must say `nonlocal`. Without it, Python thinks you are making a new local name (like in lesson 13).

Here is a step-by-step example: a function that counts how many times it was called.

1. The outer function makes `count = 0`.
2. The inner function says `nonlocal count`, adds 1 and returns it.
3. The outer function returns the inner one.

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count          # without this: UnboundLocalError
        count += 1
        return count
    return increment

c = make_counter()
print(c(), c(), c())     # -> 1 2 3

d = make_counter()       # a separate counter with its own count
print(d())               # -> 1
```

A closure can hold several remembered values, and an outer function can return more than one inner function (as a tuple), so they share the same remembered data:

```python
def make_account(balance):
    def deposit(n):
        nonlocal balance
        balance += n
        return balance
    def show():
        return balance
    return deposit, show

deposit, show = make_account(10)
deposit(5)
print(show())    # -> 15
```

### A trap: late binding

A closure remembers the **variable**, not the value it had. It reads the value when the function is **called**. (`lambda` makes a tiny function with no name. You will learn it in lesson 25.)

```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])        # -> [2, 2, 2]   all see the final i

funcs = [lambda i=i: i for i in range(3)]    # a default value is stored right away
print([f() for f in funcs])        # -> [0, 1, 2]
```

## Decorators

A **decorator** is a function that takes a function and gives back a replacement for it (usually a wrapper that does something extra before and after).

```python
import functools

def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("calling", func.__name__)
        result = func(*args, **kwargs)
        print("result:", result)
        return result
    return wrapper

@logged
def add(a, b):
    return a + b

print(add(2, 3))
# -> calling add
# -> result: 5
# -> 5
```

The line `@logged` above `def add` means exactly the same as `add = logged(add)` right after the function is defined.

What each part does:

- The `wrapper` takes `*args, **kwargs` (lesson 13), so it accepts any arguments and passes them on.
- It **returns** the result of the real function. If you forget this, the decorated function always returns `None`.
- `@functools.wraps(func)` copies the name and docstring of `func` onto `wrapper`. Without it, every decorated function is called `wrapper` in logs and error messages, and tools that read function signatures (like FastAPI) can get confused.

### Doing something around the call

Want to **time** a function? Use `time.perf_counter()`, which gives the time in seconds. Read it before and after, and subtract:

```python
import time

start = time.perf_counter()
sum(range(1_000_000))
elapsed = time.perf_counter() - start
print(elapsed < 1)    # -> True
```

To make sure the "after" part runs **even when the function raises an error**, put it in a `finally` block (lesson 21). A decorator can do all of this inside its wrapper.

### Keeping information on the wrapper

A function is an object, so it can have attributes. A decorator can store information on the wrapper, like a counter:

```python
def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0           # an attribute on the function itself
    return wrapper

@count_calls
def hello():
    return "hi"

hello(); hello()
print(hello.calls)    # -> 2
```

## Decorators with arguments

For `@repeat(3)`, you need **three** levels:

1. The outer function takes the arguments (`3`) and returns the decorator.
2. The decorator takes the function and returns the wrapper.
3. The wrapper does the work.

```python
def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def say():
    print("hey")

say()
# -> hey
# -> hey
# -> hey
```

`@repeat(times=3)` means `say = repeat(times=3)(say)`.

## Built-in decorators you should know

| Decorator | What it does |
|---|---|
| `@functools.lru_cache` / `@functools.cache` | remembers results, so the same call is not run twice (arguments must be hashable) |
| `@property`, `@classmethod`, `@staticmethod` | class tools from lesson 19 |
| `@dataclass` | a decorator for a **class** (decorators can wrap classes too) |
| `@contextlib.contextmanager` | builds context managers (next lesson) |

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(80))             # -> 23416728348467685   fast: each n is worked out once
print(fib.cache_info().hits > 0)    # -> True
```

`lru_cache` is only safe for **pure** functions: the result depends only on the arguments, and there are no side effects. It is a bad idea when:

- an argument is a list or dict (not hashable),
- the result depends on the time or a database,
- the function has side effects, like sending an email.

## How `@app.get` works

A decorator does not have to wrap the function. It can just **register** it and give it back unchanged. That is how web frameworks collect routes:

```python
class App:
    def __init__(self):
        self.routes = {}

    def get(self, path):
        def decorator(func):
            self.routes[("GET", path)] = func     # remember the function
            return func                           # give it back as it was
        return decorator

app = App()

@app.get("/hello")
def hello():
    return "hi"

print(app.routes[("GET", "/hello")]())    # -> hi
```

## Common mistakes

- Forgetting `return` in the wrapper. The decorated function then returns `None`.
- Forgetting `@functools.wraps`.
- Writing `@repeat` when the decorator needs arguments (`@repeat(3)`), or the other way round.
- Using `lru_cache` with unhashable arguments or functions with side effects.
- Changing a remembered variable without `nonlocal`.

## Interview corner

- **Q: What is a closure?** An inner function that keeps access to the variables of its outer function, even after the outer function has returned.
- **Q: Write a decorator that times a function.** Use `@functools.wraps`, `*args, **kwargs`, return the result, and record the time in a `finally` block.
- **Q: Why use `functools.wraps`?** It keeps the name, docstring and signature of the original function.
- **Q: How does a decorator with arguments work?** An outer function returns the decorator, which returns the wrapper. That is three nested functions.

## Summary

- Functions are values. Python finds names in the order Local, Enclosing, Global, Built-in.
- A closure remembers outer variables. Use `nonlocal` to change them. Beware late binding.
- `@d` above `def f` means `f = d(f)`. A wrapper uses `*args, **kwargs`, returns the result and uses `@functools.wraps`.
- A decorator with arguments is a function that returns a decorator, which returns a wrapper.
- `lru_cache` remembers results of pure functions. Registration decorators power `@app.get`.
