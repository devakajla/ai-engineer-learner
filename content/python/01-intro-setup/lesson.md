---
title: Intro & setup
summary: What Python is, how to write and run your first lines, how functions and exercises work in this app, and how to set up a project with uv.
plan_ids: [PY-10]
---

Python is a programming language. You write instructions in a text file, and Python follows them one by one. It is popular because the code is short and easy to read. It is used for websites, data work and AI.

This is lesson 1, so we start slowly. By the end you will run your first code, know how the exercises in this app work, and know how to set up a project.

## Your first program

The `print()` function shows something on the screen.

```python
print("Hello, world!")    # -> Hello, world!
print(2 + 3)              # -> 5
print("Python", "is", "fun")   # -> Python is fun
```

Text must be inside quotes. Text in quotes is called a **string**. Numbers do not need quotes.

A **comment** starts with `#`. Python ignores it. Use comments to explain your code to people.

```python
# This line is a comment. Python skips it.
print("Hi")   # a comment can also come after code
```

To ask the user for text, use `input()`. A **variable** is a name for a value (`name` below). You will learn variables in lesson 2.

```python
name = input("Your name: ")    # the user types: Dev
print("Hello,", name)          # -> Hello, Dev
```

> `input()` always gives you text (a string), even if the user types a number.

## Spaces matter in Python

Python uses **indentation** (spaces at the start of a line) to group lines together. Many other languages use `{ }` for this.

```python
name = "Dev"

if len(name) > 2:           # a colon (:) starts a group of lines
    print("long name")      # indented by 4 spaces, so it belongs to the if
print("done")               # not indented, so it is outside the if
# -> long name
# -> done
```

You will learn `if` properly in lesson 6. For now, see the rule: **the indented lines belong to the line above them.**

- Wrong indentation is an error (`IndentationError`), not a style choice.
- Use 4 spaces for each level. Do not mix tabs and spaces (`TabError`).
- Python does not need `;` at the end of a line, and you do not declare types.

## Functions and how exercises work

A **function** is a small named piece of code that you can use again and again. You give it **inputs**, it does some work, and it gives back an **answer**. You will learn functions fully in lesson 13. Here is the pattern you need now:

```python
def double(n):        # def <name>(<input>):
    return n * 2      #     return <the answer>

double(4)   # -> 8
double(10)  # -> 20
```

- `def` creates the function. The names in the brackets are its inputs.
- The indented line is the body of the function.
- `return` sends the answer back to whoever called the function.

Every exercise in this app asks you to write a function like this. Hidden tests call your function and check the answer it **returns**.

`print` and `return` are **not** the same:

```python
def show_double(n):
    print(n * 2)       # shows 6 on screen, but gives back nothing

result = show_double(3)    # -> prints 6
print(result)              # -> None   (None means "no value")
```

`print` only shows something on the screen. `return` gives the answer back to the code that called the function. The tests read the returned answer, so **always `return` your answer in exercises.**

Two small tools help with text:

```python
"Hello, " + "Dev"     # -> 'Hello, Dev'   + joins two strings
"abc".upper()         # -> 'ABC'          .upper() makes all letters capital
```

Here is a full example, step by step. We write `add_dots(text)` that returns the text with `...` at the end.

1. The input is `text`, a string.
2. We join the text and `"..."` with `+`.
3. We `return` the joined string.

```python
def add_dots(text):
    return text + "..."

add_dots("wait")    # -> 'wait...'
```

## Python and types

Every value in Python has a **type**: a whole number is an `int`, text is a `str`, and so on. You will learn the types in lesson 2.

Python is **dynamically typed**. A name does not have a type. The value has one. So a name can point to an `int` now and a `str` later:

```python
x = 10        # x is a name for the value 10
x = "ten"     # now x is a name for the text "ten". This is allowed.
print(type(x))   # -> <class 'str'>
```

Python is also **strongly typed**. It will not silently mix types that do not fit together:

```python
"5" + 5    # TypeError: can only concatenate str (not "int") to str
```

A `TypeError` means "you used a value of the wrong type here". Some other languages (like JavaScript) would quietly turn the number into text and give `"55"`. Python stops and tells you, which finds bugs early.

## Three ways to run code

| Way | Command | Good for |
|---|---|---|
| REPL (type and see the result at once) | `python` | quick experiments |
| Script (a `.py` file) | `python app.py` | real programs |
| Module | `python -m pytest` | running an installed tool with the Python you chose |

`python -m tool` runs the tool with **this exact Python**. This avoids a common bug: the `pytest` on your computer may belong to a different Python than your project uses.

## Project setup with uv

`uv` is a fast tool that manages Python versions, project folders and packages in one place. A **package** is code written by other people that you can add to your project, like `requests`.

```bash
uv init my-project      # makes a new project (pyproject.toml, main.py, .python-version)
cd my-project
uv add requests         # adds a package to your project and installs it
uv run main.py          # runs your file inside the project's own environment
uv run pytest           # runs a tool inside the project's own environment
```

A **virtual environment** (the `.venv/` folder) is a private box of packages for one project. Because of it, two projects can use different versions of the same package without clashing. You will learn more in *Packaging with uv* (Level 3).

## A little deeper (optional)

You can skip this on your first read.

**What happens when you run `python app.py`?**

1. Python **compiles** your code into **bytecode**: a list of very simple instructions. You may see it saved as `.pyc` files in a `__pycache__/` folder.
2. The **Python virtual machine** (part of the program called CPython) runs the bytecode one instruction at a time.

So Python is called "interpreted", but it does have a compile step. It compiles to bytecode, not to machine code.

```python
import dis

def add(a, b):
    return a + b

dis.dis(add)
# prints bytecode like: LOAD_FAST a, LOAD_FAST b, BINARY_OP (+), RETURN_VALUE
```

> **Interview line:** "CPython compiles source code to bytecode, and a virtual machine runs the bytecode."

## Common mistakes

- Using `print` instead of `return` in a function. The tests then get `None`.
- Mixing tabs and spaces. This gives `TabError`.
- Writing a number in quotes (`"5"`) and then using it like a number. `"5" + 5` is a `TypeError`.
- Installing packages for the whole computer with `pip install` instead of inside the project. This causes "it works on my machine" bugs.

## Summary

- `print()` shows things on the screen. `#` starts a comment. `input()` reads text.
- Indentation (4 spaces) shows which lines belong together.
- A function takes inputs and `return`s an answer. In exercises, always `return` your answer. `print` only shows it.
- Python is dynamically typed (values have types, not names) and strongly typed (no silent mixing like `"5" + 5`).
- Run code with the REPL, `python file.py` or `python -m tool`. `uv` sets up projects and packages.
- Behind the scenes, CPython compiles your code to bytecode and a virtual machine runs it.
