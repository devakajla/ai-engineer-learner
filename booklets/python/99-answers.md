# Answers to the exercises

Try each one yourself first. "Think" questions have short answers. Code answers are one possible solution.

## Chapter 1

1. `print("Dev")` and `print("Become an AI Engineer")`.
2. A comment such as `# show my name` above each line.
3. For example `print("a` gives `SyntaxError`, `prnt("a")` gives `NameError`, `"a" + 1` gives `TypeError`, and an extra space at the start of a line gives `IndentationError`.
4. Yes. Lines 1 and 2 ran and printed before the error appeared on line 3. The interpreter works line by line.

## Chapter 2

1. `print(f"{799 * 0.85:.2f}")` gives `679.15`.
2. `minutes = 135`, then `print(f"{minutes // 60} h {minutes % 60} min")` gives `2 h 15 min`.
3. `print(text.strip().lower().replace("fun", "great"))` gives `python is great` (lower-case first, so the word to replace is `fun`).
4. `print(word[0], word[-1], word[::-1])`.
5. `False`, `False`, `2`, `2.0`, `<class 'int'>`.
6. Floats are stored in binary and cannot hold 0.1 exactly, so the sum is slightly off. For prices, use whole cents or `Decimal`, or compare with a small tolerance.

## Chapter 3

1. `if score >= 90: print("A")` `elif score >= 75: print("B")` `elif score >= 50: print("C")` `else: print("F")`.
2. `total = 0` then `for n in range(1, 101): total += n`. It gives `5050`, which equals `100 * 101 // 2`.
3. `for n in range(7, 100, 7): print(n)`.
4. `count = 0` then `for w in "the cat and the hat".split(): if w == "the": count += 1`. The answer is `2`.
5. `n = 101` then `while n % 3 != 0 or n % 5 != 0: n += 1`. The answer is `105`.
6. `for i, fruit in enumerate(fruits, start=1): print(f"{i}. {fruit}")`.
7. It gives a fallback when `x` is empty. The bug is that `0` or an empty string is also falsy, so a valid `0` is replaced by the default. Use `x if x is not None else "guest"` in that case.

## Chapter 4

1. `print(max(nums), min(nums), sum(nums), nums[::-1])`.
2. `list(dict.fromkeys([4, 1, 4, 2, 1]))` gives `[4, 1, 2]`.
3. `counts = {}` then `for ch in "banana": counts[ch] = counts.get(ch, 0) + 1`. It gives `{'b': 1, 'a': 3, 'n': 2}`.
4. `a - b` gives `{1, 2}`, `a & b` gives `{3}`, `a | b` gives `{1, 2, 3, 4}`.
5. `{v: k for k, v in d.items()}` gives `{1: 'a', 2: 'b'}`.
6. Count with a dict, then `max(counts, key=counts.get)`.
7. A **set**. Membership checks are fast, and the order does not matter.

## Chapter 5

1. `def is_even(n): return n % 2 == 0`.
2. `def average(numbers): return sum(numbers) / len(numbers) if numbers else 0`.
3. `def full_name(first, last, middle=""): return " ".join(p for p in (first, middle, last) if p)`.
4. `def total(*numbers): return sum(numbers)`.
5. `def longest(words): return max(words, key=len)`.
6. The bug: `def add(x, items=[])` shared across calls. The fix: `items=None` and `if items is None: items = []`.
7. A returned value can be used by other code, stored, tested and combined. A printed value is gone once it is shown.

## Chapter 6

1. `with open("todo.txt", "w") as f: f.write("a\n")`, then `with open("todo.txt", "a") as f: f.write("b\n")`, then `for i, line in enumerate(open("todo.txt"), 1): print(i, line.strip())` (use `with` in real code).
2. `with open(path) as f: n = sum(1 for _ in f)`.
3. `json.dump(data, f)` into a file opened with `"w"`, then `json.load(f)`. Then `assert loaded == data`.
4. `def safe_int(text): try: return int(text)` `except ValueError: return None`.
5. `try: open("nofile.txt")` `except FileNotFoundError: print("File not found")`.
6. `class AppError(Exception): pass` and `class NotFound(AppError): pass`, then `try: raise NotFound("x")` `except AppError as e: print("caught", e)`.
7. It catches **everything**, including typos and `Ctrl+C`, and hides real bugs.

## Chapter 7

1. `[n * n for n in [1, 2, 3, 4, 5, 6] if n % 2 == 1]` gives `[1, 9, 25]`.
2. `[s.strip() for s in ["  a ", "b  "]]`.
3. `{w: len(w) for w in "the quick brown fox".split()}`.
4. `sorted(words, key=lambda w: (len(w), w))`.
5. `sorted(rows, key=lambda r: r["score"], reverse=True)`.
6. `[x for sub in nested for x in sub]`.
7. Use the generator form when you only go through the values once (a sum, max, or loop), because it does not build the whole list in memory.

## Chapter 8

1. `[1, 2]`. `b += [2]` changes the list in place, and `a` points to the same list.
2. `def with_tax(prices): return [p * 1.18 for p in prices]`. It builds a new list and does not change the input.
3. A shallow copy shares the inner lists, so changing an inner item shows in the original and the shallow copy, but not in the deep copy.
4. Right: `[[0] * 3 for _ in range(3)]`. Wrong: `[[0] * 3] * 3` has three references to the same row, so changing one changes all.
5. Define `__repr__` returning `f"P({self.name!r})"` and `__eq__` comparing the names. Printing a list shows `[P('a')]`.
6. A tuple of immutable items can be hashed. A tuple that holds a list contains something that can change, so it cannot be hashed.

## Chapter 9

1. In `withdraw`: `if amount > self.balance: raise ValueError("not enough money")`, otherwise `self.balance -= amount`.
2. `class Shape(ABC)` with an abstract `area`, then `Circle` returns `3.14159 * r * r` and `Rectangle` returns `w * h`.
3. `@dataclass class Person: name: str; age: int; city: str`.
4. A `@property` for the value and a setter that raises `ValueError` when it is below `-273.15`.
5. `class Library: def __init__(self): self.books = []` and methods such as `add` that use `self.books`. A Library **has** a list of books.
6. **S**, single responsibility. The class has three reasons to change.

## Chapter 10

1. `def evens_up_to(n): for i in range(0, n + 1, 2): yield i`.
2. `def read_lines(path): with open(path) as f: for line in f: yield line.strip()`.
3. `list(islice((n * 10 for n in count() if n % 3 == 0), 4))` gives `[0, 30, 60, 90]`.
4. `def fib(): a, b = 0, 1` then `while True: yield a; a, b = b, a + b`. Use `islice(fib(), 10)`.
5. `g = (n for n in range(3)); list(g)` gives `[0, 1, 2]`, and a second `list(g)` gives `[]`.
6. Both give out one piece at a time as soon as it is ready, and neither needs the full result in memory.

## Chapter 11

1. `def make_adder(n): def add(x): return x + n` and `return add`.
2. Return both `inc` and `reset` functions that use `nonlocal count`, or one function that takes an optional argument.
3. A decorator that does `start = time.perf_counter()`, calls the function, and prints `time.perf_counter() - start`. Use `functools.wraps`.
4. `print(fn.__name__, args, kwargs)` before calling `fn(*args, **kwargs)`.
5. `@retry(times=3)` is three layers: `retry(times)` returns `decorator(fn)` which returns `wrapper`. The wrapper loops `for attempt in range(times)`, uses `try: return fn(...)`, and `except Exception: if attempt == times - 1: raise`.
6. The second identical call is nearly instant because the result comes from the cache.
7. The wrapper accepts `*args, **kwargs` and simply passes them on, so it does not need to know the function's real parameters.

## Chapter 12

1. `@contextmanager def timer(): start = time.perf_counter()` then `try: yield` `finally: print(time.perf_counter() - start)`.
2. `__enter__` saves `os.getcwd()` and calls `os.chdir(new)`. `__exit__` calls `os.chdir(saved)`.
3. `with suppress(FileNotFoundError): os.remove(path)`.
4. Raise an error inside a `with` block of a context manager that prints in `__exit__` (or `finally`). The message still prints.
5. A FastAPI `yield session` dependency opens the session, hands it to the route and closes it afterwards. That is the same setup and cleanup shape as a context manager.

## Chapter 13

1. For example `def add(a: int, b: int) -> int:`.
2. `class Product(BaseModel): name: str = Field(min_length=1); price: float = Field(gt=0); tags: list[str] = Field(default_factory=list)`.
3. `price` becomes the float `12.5`, and `tags` is `[]`.
4. `for e in err.errors(): print(e["loc"], e["msg"])`.
5. A `field_validator("tags")` returning `[t.lower() for t in value]`.
6. Model output is text that may be wrong. Validating catches broken or missing fields at once, and you can ask the model to try again.

## Chapter 14

1. Sequential: 5 x 0.5 = 2.5 s. With a pool of 5 threads: about 0.5 s.
2. Expect no gain with threads and a real gain with processes (about the number of free cores, less the start-up cost).
3. Often the unlocked version still prints `400000` on a modern machine, because races are random and rare. That is exactly why they are dangerous. Use the lock anyway.
4. For example: calling an API (I/O), resizing images (CPU), reading a big file (I/O), parsing huge text (CPU).
5. A new process imports your file again. Without the guard, it would start new processes forever.

## Chapter 15

1. About 5 s one by one, about 1 s with `gather`.
2. 9 jobs in groups of 3 means 3 rounds, so about 3 s.
3. `try: await asyncio.wait_for(job(), 0.5)` `except asyncio.TimeoutError: print("too slow")`.
4. The list contains the normal results and the exception object, for example `[2, ValueError('x'), 6]`.
5. `async def ticks(): for i in range(5): await asyncio.sleep(0.1); yield i`, then `async for i in ticks(): print(i)`.
6. `await asyncio.sleep` hands control back to the event loop, so others run. `time.sleep` holds the thread, so nothing else can run.

## Chapter 16

1. `assert is_even(4)`, `assert is_even(0)`, `assert not is_even(-3)`.
2. `@pytest.mark.parametrize("text, want", [("Hello World", "hello-world"), ...])`.
3. `assert safe_int("abc") is None` and `with pytest.raises(ValueError): int("abc")`.
4. The test receives `tmp_path`, calls the function with `tmp_path / "out.txt"` and reads the file back.
5. The function calls `client.get(...)`. In the test pass `class FakeClient: def get(self, url): return "fake"`.
6. It is slow, costs money, can fail for reasons outside your code, and gives different answers each time.

## Chapter 17

1. `timeit.timeit(lambda: 9999 in L, number=1000)` against the same with a set. The set is far faster.
2. In the profile table, the helper has a high `ncalls` and a large `cumtime`.
3. `"".join(parts)` against `s += part`. The join is much faster for many pieces.
4. `@functools.lru_cache(maxsize=None)` above `def fib(n)`.
5. N+1: one call per user. Fetch the orders of all users in one query (`WHERE user_id IN (...)`) and group them in Python.
6. You may spend time on code that is not the problem, and make it harder to read for no gain.

## Interview drills (chapter 18)

**1. Reverse a string without `[::-1]`**

```python
def reverse(text):
    result = ""
    for ch in text:
        result = ch + result
    return result

print(reverse("python"))
# -> nohtyp
```

**2. Most frequent character**

```python
def most_common_char(text):
    counts = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    return max(counts, key=counts.get)

print(most_common_char("banana"))
# -> a
```

**3. Anagrams**

```python
def is_anagram(a, b):
    return sorted(a.lower()) == sorted(b.lower())

print(is_anagram("Listen", "Silent"))
# -> True
```
