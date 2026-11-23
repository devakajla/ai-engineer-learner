---
title: Functions, args & scope
summary: Write reusable functions, pass values in different ways, return answers, and understand where names live.
plan_ids: []
---

A **function** is a named block of code that you can run many times. Functions stop you from repeating yourself, they give an idea a name, and they are the unit that tests (and exercises!) check. You met the basic pattern in lesson 1. Now we go through it slowly.

## Define and call

```python
def greet(name):
    return "Hello, " + name

message = greet("Dev")
print(message)   # -> Hello, Dev
```

- `def name(parameters):` starts the function. The indented lines are its **body**.
- To **call** (run) the function, write its name and brackets: `greet("Dev")`.
- `return` sends a value back and ends the function.

Without `return`, a function gives back `None`:

```python
def say_hi():
    print("hi")

result = say_hi()    # prints: hi
print(result)        # -> None
```

> `print` shows something on the screen. `return` gives a value back to the code that called the function. Beginners often mix these up.

## Parameters and arguments

The names in the `def` line are **parameters**. The values you pass when calling are **arguments**.

```python
def power(base, exponent):
    return base ** exponent

power(2, 3)                    # -> 8   by position
power(exponent=3, base=2)      # -> 8   by name (any order)
power(2, exponent=3)           # -> 8   mixed: positional ones first
```

### Default values

Give a parameter a **default** value, and the caller may leave it out:

```python
def welcome(user, place="home"):
    return f"Welcome to {place}, {user}"

welcome("Dev")               # -> 'Welcome to home, Dev'
welcome("Dev", "the app")    # -> 'Welcome to the app, Dev'
```

Parameters with a default must come **after** the ones without.

### The mutable default trap

A default value is created **once**, when the function is defined, not on every call. With a list, this causes a surprise:

```python
def add(item, bucket=[]):      # BAD
    bucket.append(item)
    return bucket

add(1)   # -> [1]
add(2)   # -> [1, 2]   surprise: the same list is used again!
```

The fix: use `None` as the default and make the list inside the function:

```python
def add(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

## `*args` and `**kwargs`

Sometimes you do not know how many values a caller will pass.

- `*args` collects extra positional arguments into a **tuple**.
- `**kwargs` collects extra keyword arguments (`name=value`) into a **dict**.

```python
def show(*args, **kwargs):
    print(args, kwargs)

show(1, 2, color="red")   # -> (1, 2) {'color': 'red'}
show()                    # -> () {}
```

(The names `args` and `kwargs` are just a habit. The stars are what matter.)

Because `args` is a tuple and `kwargs` is a dict, all the tools you know already work on them: `len`, `sum`, loops, `sorted` and so on. Remember that looping over a dict (or using `sorted` on it) gives its **keys**:

```python
sorted({"b": 1, "a": 2})    # -> ['a', 'b']
```

Here is a function that adds up any number of values:

```python
def total(*numbers):
    return sum(numbers)

total(1, 2, 3)   # -> 6
total()          # -> 0
```

The same stars work when you **call** a function. They unpack a list or a dict into arguments:

```python
nums = [1, 2, 3]
total(*nums)                       # the same as total(1, 2, 3)

opts = {"base": 2, "exponent": 5}
power(**opts)                      # the same as power(base=2, exponent=5)
```

### Keyword-only parameters

Parameters after a lone `*` can only be given by name:

```python
def connect(host, *, port=5432, timeout=10):
    return f"{host}:{port}"

connect("db", port=1234)    # -> 'db:1234'
connect("db", 1234)         # TypeError: takes 1 positional argument but 2 were given
```

## Returning several values

A function can return more than one value. Python packs them into a tuple, and you unpack them (lesson 9):

```python
def min_max(nums):
    return min(nums), max(nums)

low, high = min_max([3, 1, 7])
print(low, high)    # -> 1 7
```

## Scope: where names live

A **scope** is the place where a name can be used.

- A name made **inside** a function is **local**. It exists only there.
- Code inside a function can **read** names from outside it.

```python
rate = 0.2            # outside any function (a global name)

def tax(amount):
    fee = amount * rate     # reads the global name
    return fee

print(tax(100))   # -> 20.0
print(fee)        # NameError: fee only existed inside tax
```

If you **assign** to a name inside a function, Python treats it as local, even when a global name is the same:

```python
count = 0

def bump():
    count = count + 1      # UnboundLocalError: count is local here, but it has no value yet

bump()
```

The better way: pass values in and return values out.

```python
def bump(count):
    return count + 1

count = bump(count)   # now 1 (when count was 0)
```

## A little deeper (optional)

**Docstrings.** A string on the first line of a function explains it. `help(area)` shows it.

```python
def area(width, height):
    """Return the area of a rectangle."""
    return width * height
```

**Type hints.** You can add hints like `width: float`. You will learn them in Level 2.

**Positional-only parameters.** A `/` in the signature makes the parameters before it positional-only: `def f(a, b, /, c)`.

**The LEGB rule.** For a name, Python looks in this order: Local, Enclosing function, Global, Built-in.

**The `global` keyword.** `global count` inside a function lets you assign to the global name. It works, but avoid it.

**Functions are values.** You can store a function in a variable or pass it to another function:

```python
def shout(text):
    return text.upper() + "!"

f = shout
f("hi")                                   # -> 'HI!'
sorted(["b", "A", "c"], key=str.lower)    # -> ['A', 'b', 'c']
```

## Common mistakes

- Using a mutable default argument (`def f(x, items=[])`).
- Forgetting `return`. The function then gives back `None`.
- Using `print` instead of `return`, and then trying to use the result.
- Assigning to an outside name inside a function, which gives `UnboundLocalError`.
- Writing `greet` instead of `greet()`. `greet` is the function itself. `greet()` calls it.
- Making one function do too many things. One function should do one job.

## Summary

- `def name(params): ... return value`. No `return` means `None`.
- Arguments can be positional, keyword, default (never a mutable default), `*args` (a tuple) or `**kwargs` (a dict). Parameters after a lone `*` are keyword-only.
- Return several values as a tuple and unpack them.
- Names made inside a function are local. Reading outside names is fine, and assigning makes a new local name.
- Prefer parameters and return values over `global`.
