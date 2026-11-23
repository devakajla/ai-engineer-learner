---
title: Level 1 interview questions
summary: The Level 1 topics as interviewers ask them, with follow-up questions, short model answers and three timed coding exercises.
plan_ids: [PY-07]
---

An interview asks you to **explain** what you know. This lesson shows the Level 1 topics the way interviewers ask about them.

How to use it: **answer each question out loud first** (or type it to Claude in the side panel and ask for feedback). Then read the model answer. Interviewers rarely stop after the first answer. They ask follow-up questions, so the usual follow-ups are listed too.

Some words you will see:

- **Falsy**: a value that acts like `False` in a condition (`0`, `""`, `[]`, `None`).
- **Hashable**: a value that cannot change, so it can be a dict key or a set member.
- **Shallow copy**: a new outer container, whose inner items are still shared with the original.
- **Complexity**: how much slower code gets as the data gets bigger. `O(1)` means about the same time for any size. `O(n)` means the time grows with the number of items.

## 1. Types and truthiness

**Q: What is printed and why?**

```python
print(0.1 + 0.2 == 0.3)
print(bool("False"), bool([]))
```

**A:** `False`, then `True False`. Decimal numbers are stored in binary and are not exact (`0.1 + 0.2` is `0.30000000000000004`), so compare them with `math.isclose`, or use `decimal` for money. `"False"` is a non-empty string, so it is truthy. An empty list is falsy.

- *Follow-up: What counts as falsy?* → `False`, `None`, zero numbers, and empty strings and containers.
- *Follow-up: `is` vs `==`?* → `==` compares values. `is` asks if it is the very same object. Use `is` only for `None`.
- *Follow-up: Is `True == 1`?* → Yes. `bool` is a kind of `int`.

## 2. Strings

**Q: Strings cannot change. What does that mean when you build a big string in a loop?**

**A:** `s += x` in a loop can make a new string every time, which is slow. Collect the pieces in a list and use `"".join(parts)` once.

- *Follow-up: What do string methods return?* → New strings. `s.upper()` does not change `s`.
- *Follow-up: f-strings vs `format` vs `%`?* → f-strings are the modern choice: easy to read and fast. `f"{x=}"` helps with debugging.
- *Follow-up: How do you reverse a string?* → `s[::-1]`.

## 3. Lists, tuples, sets and dicts

**Q: When do you choose a list, a tuple, a set or a dict?**

**A:** List: an ordered collection that can change. Tuple: a fixed record. It is hashable, so it can be a dict key. Set: unique items, fast "is it in here?" checks, and set maths. Dict: look things up by key.

- *Follow-up: How fast is `x in list` vs `x in set`?* → `O(n)` vs about `O(1)`. Turn a list into a set when you check membership many times.
- *Follow-up: What can be a dict key?* → A hashable value: a string, a number, or a tuple of hashable values. Not a list or a dict.
- *Follow-up: Are dicts ordered?* → Yes. They keep insertion order (Python 3.7 and later).
- *Follow-up: `append` vs `extend`?* → `append` adds one item (even a list). `extend` adds each element.
- *Follow-up: `sort()` vs `sorted()`?* → `sort` changes the list and returns `None`. `sorted` returns a new list from any iterable.

## 4. Copies and references

**Q: What does this print?**

```python
a = [1, 2]
b = a
b.append(3)
c = a[:]
c.append(4)
print(a, c)
```

**A:** `[1, 2, 3] [1, 2, 3, 4]`. `b = a` is a second name for the same list. `a[:]` is a (shallow) copy.

- *Follow-up: Shallow vs deep copy?* → A shallow copy makes a new outer container, but the inner items are shared. `copy.deepcopy` copies everything. Level 2 goes deeper.

## 5. Loops and comprehensions

**Q: Rewrite this loop as a comprehension. When would you not?**

```python
result = []
for n in nums:
    if n % 2 == 0:
        result.append(n * n)
```

**A:** `result = [n * n for n in nums if n % 2 == 0]`. Use a plain loop when there are several conditions, side effects, or the comprehension is hard to read.

- *Follow-up: Where do `if` and `if/else` go?* → A filter `if` goes at the end. A choice (`a if c else b`) goes at the front.
- *Follow-up: List comprehension vs generator expression?* → `[...]` builds the whole list. `(...)` makes one item at a time, which is good inside `sum`, `any` and `all` for big data.
- *Follow-up: What does `for ... else` do?* → The `else` runs if the loop finished without `break`.

## 6. Functions and scope

**Q: What is wrong with this function?**

```python
def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags
```

**A:** The default list is created once, and every call shares it. Use `tags=None` and create a new list inside the function.

- *Follow-up: What do `*args` and `**kwargs` give you?* → A tuple of extra positional arguments, and a dict of extra keyword arguments.
- *Follow-up: Explain LEGB.* → Python looks up a name in this order: Local, Enclosing, Global, Built-in. Assigning to a name inside a function makes it local.
- *Follow-up: Does Python pass by value or by reference?* → Neither exactly. The function gets a reference to the object. Changing a mutable argument is visible to the caller. Pointing the name at a new object is not.
- *Follow-up: What does a function without `return` give back?* → `None`.

## 7. Modules, files and errors

**Q: What does `if __name__ == "__main__":` do, and why use it?**

**A:** It runs the block only when the file is run directly, not when it is imported. So a file can be both a library and a program, and nothing runs by accident at import time.

- *Follow-up: Why use `with open(...)`?* → It closes the file for you, even when there is an error.
- *Follow-up: What do `try`, `except`, `else` and `finally` do?* → `except` handles errors. `else` runs only if there was no error. `finally` always runs, for cleanup.
- *Follow-up: Why is a bare `except:` bad?* → It catches everything (even `Ctrl+C`) and hides bugs. Catch specific errors.
- *Follow-up: EAFP vs LBYL?* → Try and handle the failure, or check before acting. Python often prefers EAFP.
- *Follow-up: `import x` vs `from x import y`?* → The first keeps the module name (`x.y`). The second brings the name in directly. Avoid `import *`.

## 8. Rapid-fire (one-liners)

| Question | Short answer |
|---|---|
| `//` vs `/` | floor division vs true division (always a float) |
| `-7 // 2` | `-4` (it rounds down) |
| Mutable vs immutable types | mutable: list, dict, set. Immutable: int, str, tuple, frozenset |
| Swap two variables | `a, b = b, a` |
| Empty set | `set()`. `{}` is an empty dict |
| `x = x.sort()` | sets `x` to `None` |
| `range(5)` | 0, 1, 2, 3, 4 |
| Remove duplicates, keep order | `list(dict.fromkeys(items))` |
| Merge two dicts | `{**a, **b}` (or `a \| b` on 3.9+) |
| Read a file line by line | `for line in f:` inside `with open(...)` |

## Tools for the coding exercises

The three coding exercises use tools you already know. Here are two patterns that help, shown on different problems.

**Pattern 1: remember what you have seen, in a dict.** A dict looks things up fast. Loop once, and for each item ask the dict a question about the items before it. Example: find the first word that appears twice, and the position where it first appeared.

```python
words = ["cat", "dog", "bird", "dog"]
first_seen = {}                       # word -> position
for i, word in enumerate(words):
    if word in first_seen:
        print(word, first_seen[word])     # -> dog 1
        break
    first_seen[word] = i
```

**Pattern 2: rank things with `sorted` and tuples.** When `sorted` compares two tuples, it compares the first items, and if they are equal, the second items, and so on. To put the biggest number first, put a minus sign in front of it:

```python
sorted([(2, "b"), (3, "c"), (3, "a")])        # -> [(2, 'b'), (3, 'a'), (3, 'c')]
sorted([(-2, "b"), (-3, "c"), (-3, "a")])     # -> [(-3, 'a'), (-3, 'c'), (-2, 'b')]
```

In the second list, the biggest numbers come first (because `-3` is smaller than `-2`), and a tie is broken by the letter.

To compare two groups of letters, sort the letters of each and compare the two lists with `==`.

## How to practise

1. Do the three coding exercises here **under time pressure** (10 to 15 minutes each), like in a real interview.
2. Say the complexity out loud before you run the tests.
3. Ask Claude: *"Act as an interviewer. Ask me 5 follow-up questions on dictionaries, one at a time, and grade my answers."*
