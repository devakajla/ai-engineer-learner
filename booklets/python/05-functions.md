# 5. Functions

A **function** is a named, reusable piece of code. You write the steps once, give them a name, and then use that name whenever you need those steps. You have already used functions that others wrote: `print`, `len`, `range`.

Why they matter: without functions you copy and paste code, and when you find a bug you must fix it in ten places. With a function, you fix it once. Functions also let you give a name to an idea ("calculate tax"), which makes code read like a story.

## Defining and calling

```python
def add(a, b):
    return a + b

print(add(2, 3))
# -> 5
```

- `def` starts the definition. `add` is the name.
- `a` and `b` are **parameters**: placeholders for the inputs.
- The indented block is the **body**: what the function does.
- `return` sends a value **back** to whoever called the function and ends the function.
- `add(2, 3)` is the **call**. The real values `2` and `3` are called **arguments**.

Defining a function does not run it. It only teaches Python the recipe. The code runs when you call it.

@@ flow | Figure 5.1: a function is a machine with inputs and an output.
Arguments|2, 3|blue -> add(a, b)|the body runs|yellow -> Return value|5|green
@@ end

### `return` vs `print`

Beginners mix these up. `print` **shows** something on the screen for a human. `return` **hands a value back** to the code so it can use it. A function that only prints cannot be used inside a calculation.

If a function reaches the end without `return`, it gives back `None`:

```python
def nothing():
    pass

print(nothing())
# -> None
```

Returning several values really returns one **tuple**, which you can unpack:

```python
def min_max(items):
    return min(items), max(items)

low, high = min_max([3, 1, 2])
print(low, high)
# -> 1 3
```

## Parameters in detail

### Default values

A parameter can have a default, used when the caller does not give one:

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Asha"))
# -> Hello, Asha!
print(greet("Asha", "Hi"))
# -> Hi, Asha!
print(greet(greeting="Yo", name="Ravi"))
# -> Yo, Ravi!
```

Arguments can be **positional** (matched by order) or **keyword** (matched by name, `greeting="Yo"`). With keywords the order does not matter. Parameters with defaults must come **after** those without.

### `*args` and `**kwargs`

Sometimes you do not know how many arguments will come. `*args` collects extra positional arguments into a **tuple**. `**kwargs` collects extra keyword arguments into a **dict**.

```python
def show(*args, **kwargs):
    return args, kwargs

print(show(1, 2, x=3))
# -> ((1, 2), {'x': 3})
```

The star works in reverse too, at the call: `add(*[1, 2])` spreads a list into separate arguments, and `add(**{"a": 1, "b": 2})` spreads a dict into keyword arguments. You will see `*args, **kwargs` all over frameworks like FastAPI.

### The mutable default trap

This is the most famous Python gotcha, and a very common interview question.

```python
def bad(x, items=[]):
    items.append(x)
    return items

print(bad(1), bad(2))
# -> [1, 2] [1, 2]
```

Surprise: the second call remembered the first. Why? The default value `[]` is created **once**, when the function is *defined*, not each time it is called. Every call that uses the default shares that one list.

The fix: use `None` as the default and create a fresh list inside.

```python
def good(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items

print(good(1), good(2))
# -> [1] [2]
```

## Scope: where a name lives

A variable created **inside** a function exists only inside it (it is **local**). Outside code cannot see it, and it does not touch a variable with the same name outside.

```python
x = 10

def show():
    x = 5
    return x

print(show(), x)
# -> 5 10
```

Two different `x` values. The function's `x` is its own. Python looks for a name first inside the function, then outside (this lookup order is called LEGB; we meet it fully in chapter 11). Good functions take what they need as **parameters** and give results by **return**, instead of reaching out to change outside variables.

## `lambda`: tiny one-line functions

A `lambda` is a small nameless function for simple jobs:

```python
square = lambda n: n * n
print(square(4))
# -> 16
```

Its main use is as a short argument, like a sorting rule:

```python
words = ["bb", "a", "ccc"]
print(sorted(words, key=len))
# -> ['a', 'bb', 'ccc']
print(max(words, key=lambda w: w[-1]))
# -> ccc
```

`key=` tells `sorted`, `max` and `min` **what to compare**. Here `key=len` means "compare by length". For anything longer than one expression, write a normal `def`.

## Docstrings and good function design

A **docstring** is a text right under the `def` line that says what the function does. Tools and editors show it.

```python
def average(numbers):
    """Return the average of a list of numbers."""
    return sum(numbers) / len(numbers)
```

Habits of good functions: **one job** each, a **clear name** (a verb: `calculate_tax`), few parameters, and no surprises (do not secretly change the caller's data).

## Worked example: build a function step by step

Problem: write `count_words(text)` that returns a dict of how many times each word appears, ignoring case.

1. Decide input and output. Input: a string. Output: a dict.
2. Plan using patterns we know: **counter dict** (chapter 4), after lower-casing and splitting.
3. Write it.
4. Test with a normal case and an edge case.

```python
def count_words(text):
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts

print(count_words("The cat and the hat"))
# -> {'the': 2, 'cat': 1, 'and': 1, 'hat': 1}
print(count_words(""))
# -> {}
```

The empty string is an edge case. It returns an empty dict, which is right, and it did not crash. Make this your habit: after the normal example, try empty and one-item inputs.

::: {.box .checkpoint}
**Checkpoint:** you can explain `return` vs `print`, why `items=[]` is dangerous, and what `*args` and `**kwargs` collect.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Using `print` where you needed `return`.
- Mutable default arguments (`[]`, `{}`).
- Forgetting to **call** the function (`add` without brackets is just the function object).
- Changing a global variable from inside a function instead of returning a value.
- A function that does five jobs.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is the mutable default argument problem?** Default values are created once at definition time, so a mutable default is shared across calls. Use `None` and create inside.

**Q: What are `*args` and `**kwargs`?** They gather extra positional arguments into a tuple and extra keyword arguments into a dict.

**Q: Parameter vs argument?** A parameter is the name in the definition. An argument is the real value passed in a call.

**Q: What does a function return without `return`?** `None`.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write `is_even(n)` that returns `True` or `False`.
2. Write `average(numbers)` that returns `0` for an empty list instead of crashing.
3. Write `full_name(first, last, middle="")` that skips the middle name when empty.
4. Write `total(*numbers)` that adds any number of arguments.
5. Write `longest(words)` using `max` with a `key`.
6. Show the mutable default bug on purpose, then fix it.
7. **Think:** why is it better for a function to `return` a result than to `print` it?
:::
