# 11. Closures, decorators and functools

This chapter has three ideas that build on each other. A **closure** is a function that remembers. A **decorator** uses a closure to wrap extra behaviour around another function. `functools` gives you ready-made tools for this. Decorators are everywhere in FastAPI (`@app.get(...)`), so this is essential.

## Functions are values

In Python a function is an object, like a number. You can store it in a variable, pass it to another function, and return it from a function.

```python
def shout(text):
    return text.upper()

speak = shout
print(speak("hi"))
# -> HI
```

`speak = shout` (no brackets) gives the function a second name. Without brackets we are **not calling** it, just pointing to it. You have already used this idea with `sorted(words, key=len)`: `len` is passed as a value.

## Scope: LEGB

When Python meets a name, it looks for it in four places, in this order:

1. **L**ocal: inside the current function.
2. **E**nclosing: inside any function that wraps this one.
3. **G**lobal: at the top of the file.
4. **B**uilt-in: names Python provides, like `len`.

It uses the first match. This lookup order is the reason closures work.

## Closures: a function that remembers

You can define a function **inside** another function. The inner one can use the outer one's variables, and it keeps them even after the outer function has finished.

```python
def make_multiplier(n):
    def multiply(x):
        return x * n
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5), triple(5))
# -> 10 15
```

What happened, step by step: `make_multiplier(2)` ran and returned the inner function `multiply`. The call finished, so `n` should have vanished, but `multiply` **kept** its own copy of `n = 2`. That remembered variable is the **closure**. `double` and `triple` are two separate functions, each with its own `n`.

@@ grid 2 | Figure 11.1: each inner function carries its own remembered value.
double|multiply with n = 2;the box it remembers|blue
triple|multiply with n = 3;a different box|green
@@ end

To **change** a remembered variable from inside, declare it `nonlocal`:

```python
def counter():
    count = 0
    def inc():
        nonlocal count
        count += 1
        return count
    return inc

tick = counter()
print(tick(), tick(), tick())
# -> 1 2 3
```

Without `nonlocal`, `count += 1` would create a new local variable and fail. The counter keeps its state between calls **without a class**.

### The loop trap

```python
funcs = [lambda: n for n in range(3)]
print([f() for f in funcs])
# -> [2, 2, 2]
```

All three functions see the **same** `n`, and by the time you call them the loop has ended with `n = 2`. Closures remember the *variable*, not its value at that moment. Freeze the value with a default argument:

```python
funcs = [lambda n=n: n for n in range(3)]
print([f() for f in funcs])
# -> [0, 1, 2]
```

## Decorators

A **decorator** is a function that takes a function and returns a better version of it. It lets you add behaviour (timing, logging, checking login) without touching the function's own code.

The manual way first. We wrap `add` with a function that prints a message after it runs:

```python
def announce(fn):
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        print(fn.__name__, "done")
        return result
    return wrapper

def add(a, b):
    return a + b

add = announce(add)
print(add(1, 2))
# -> add done
# -> 3
```

Read it slowly. `announce` receives a function and builds `wrapper`, a closure that remembers `fn`. `wrapper` accepts any arguments (`*args, **kwargs`, chapter 5), calls the real function, adds its extra behaviour, and returns the result. Then `add = announce(add)` replaces `add` with the wrapped version.

The `@` line is **just a shortcut** for that last step:

```python
@announce
def add(a, b):
    return a + b
```

`@announce` above `def add` means exactly `add = announce(add)`.

@@ flow | Figure 11.2: a decorator wraps a function.
Caller|calls add(1, 2)|blue -> wrapper|extra behaviour;before and after|yellow -> real add|does the work|green
@@ end

### Keep the function's identity: `functools.wraps`

After wrapping, `add.__name__` would say `"wrapper"` and the docstring is lost. Fix it by decorating the wrapper with `functools.wraps`:

```python
import functools

def announce(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        print(fn.__name__, "done")
        return result
    return wrapper

@announce
def add(a, b):
    "adds two numbers"
    return a + b

print(add(1, 2), add.__name__, add.__doc__)
# -> add done
# -> 3 add adds two numbers
```

Always use `@functools.wraps(fn)` in your decorators. Tools like FastAPI rely on the real name and signature.

### Decorators with arguments

For `@repeat(3)` you need **one more level**: a function that takes the setting and *returns* the decorator.

```python
def repeat(times):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return [fn(*args, **kwargs) for _ in range(times)]
        return wrapper
    return decorator

@repeat(2)
def hi():
    return "hi"

print(hi())
# -> ['hi', 'hi']
```

Three layers: `repeat(2)` returns `decorator`, `decorator(hi)` returns `wrapper`. It looks scary, but each level just holds one thing: the setting, the function, then the call.

## `functools`: ready-made helpers

**`lru_cache`** remembers results, so a repeat call with the same arguments costs nothing:

```python
@functools.lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(50))
# -> 12586269025
```

Without the cache, `fib(50)` would take ages because it recomputes the same values billions of times. With it, each value is computed once. This idea is called **memoization**.

**`partial`** fixes some arguments of a function in advance:

```python
from_binary = functools.partial(int, base=2)
print(from_binary("101"))
# -> 5
```

**`reduce`** folds a list into one value: `functools.reduce(lambda a, b: a + b, [1, 2, 3])` gives `6`. A plain loop or `sum` is usually clearer.

## Where you will meet decorators

`@property`, `@staticmethod`, `@dataclass` (chapter 9), and in FastAPI `@app.get("/")`, which **registers** your function as a route. Frameworks use decorators because they can take your function and record or wrap it without you writing extra code.

::: {.box .checkpoint}
**Checkpoint:** you can explain what a closure remembers, rewrite `@decorator` as `f = decorator(f)`, and say why `functools.wraps` is used.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Forgetting `return wrapper` (the decorated name becomes `None`).
- Forgetting to return the result from `wrapper`, so the function seems to return `None`.
- Forgetting `functools.wraps`.
- Writing `@repeat` instead of `@repeat(2)` for a decorator with arguments.
- The late-binding loop trap with lambdas.
- Forgetting `nonlocal` when changing a remembered variable.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is a closure?** An inner function that keeps access to variables of the function that created it, even after that function has returned.

**Q: What is a decorator?** A function that takes a function and returns a modified one. `@d` above `def f` equals `f = d(f)`.

**Q: Why `functools.wraps`?** It copies the name, docstring and metadata to the wrapper, so the decorated function still looks like the original.

**Q: What is `lru_cache`?** A decorator that caches results by arguments, trading memory for speed.

**Q: What does LEGB stand for?** Local, Enclosing, Global, Built-in: the order of name lookup.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write `make_adder(n)` that returns a function adding `n` to its argument.
2. Write a `counter` closure with `nonlocal` that also has a way to reset.
3. Write a `@timer` decorator that prints how long a function took (`time.perf_counter`).
4. Write `@log_calls` that prints the name and arguments before each call.
5. Write `@retry(times=3)` that re-runs a function when it raises.
6. Use `lru_cache` on a slow function and compare the time of two identical calls.
7. **Think:** why can a decorator work on any function, regardless of its arguments?
:::
