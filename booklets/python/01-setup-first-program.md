# 1. Setup, your first program, and how Python runs

Before any code, you need a picture in your head of what Python **is**. Most beginners skip this and later feel lost. This chapter is short, but it makes every later chapter easier.

## What is a program?

A program is a **list of instructions** written in a language the computer can follow. A recipe is the same idea: do step 1, then step 2, then step 3, in order.

Computers do not understand English. They understand only tiny electrical on/off patterns. Programming languages sit in between: you write something humans can read, and a tool translates it.

## What is Python?

Python is a programming language that is known for being **easy to read**. The same idea takes fewer lines than in most languages. That is why it is the main language for AI and data work, and why it is popular for web backends (FastAPI).

There is also a second Python word you must know: the **interpreter**. This is the program that reads your file and does what it says, one line at a time, from top to bottom.

@@ flow | Figure 1.1: what happens when you run a Python file.
Your file|hello.py;text you wrote|blue -> Interpreter|the python program;reads line by line|yellow -> Result|printed text, files,;network calls|green
@@ end

Think of the interpreter as a **translator who reads your recipe aloud and cooks as they read**. If there is a mistake on line 5, lines 1 to 4 have already run. This is why error messages mention a line number.

## Setting up

You need two things: Python itself, and a way to manage your projects. We use **uv**, a modern tool that does both.

Why a tool at all? Different projects need different library versions. If everything is installed in one place, projects break each other. A **virtual environment** is a private folder of libraries for one project. `uv` creates and manages it for you, so you do not think about it.

```bash
uv --version
# -> uv 0.x.y
uv init hello-python
cd hello-python
```

`uv init` made a small project folder with a `main.py` file and a `pyproject.toml` file. The second file is the project's ID card: its name, its Python version and its libraries.

## Your first program

Open `main.py` and replace everything with one line:

```python
print("Hello, Dev!")
```

Run it:

```bash
uv run main.py
# -> Hello, Dev!
```

What just happened, in words:

- `print` is a **function**, a named, ready-made action. Python already knows it.
- The parentheses `( )` mean "do it now". Whatever is inside is what you give to the action.
- `"Hello, Dev!"` is **text**. The quote marks tell Python "this is words, not a command".
- `uv run main.py` started the interpreter on your file. It read one line, did it, and stopped.

## Comments

A comment is a note for **humans**. Python ignores it. Start it with `#`.

```python
# say hello to the user
print("Hello")   # this part after the hash is also ignored
```

Write comments to explain **why** you did something. Do not repeat what the code already says.

## Reading an error

Mistakes will happen all the time. This is normal, even for experts. The skill is **reading** the message.

```python
print("Hello)
```

```
  File "main.py", line 1
    print("Hello)
          ^
SyntaxError: unterminated string literal (detected at line 1)
```

Read errors from the **bottom**. The last line says the kind of error (`SyntaxError`) and what is wrong (the text was never closed). The lines above tell you where.

| Error name | Usually means |
| --- | --- |
| `SyntaxError` | you broke the grammar: a missing quote or bracket |
| `NameError` | you used a name Python does not know (often a typo) |
| `TypeError` | you mixed types that do not go together, like `"a" + 1` |
| `IndentationError` | your spaces at the start of a line are wrong |

## Indentation matters

In many languages, curly braces mark a group of lines. Python uses **spaces at the start of the line** instead. Lines that belong together have the same indentation. You will see this from chapter 3 onward.

```python
print("one")
    print("two")
# -> IndentationError: unexpected indent
```

The rule: use 4 spaces per level, and never mix spaces and tabs.

## Python 2 vs Python 3

Old tutorials sometimes show `print "hello"` without brackets. That is Python 2, which is dead. We use Python 3 only, version 3.12 or newer.

::: {.box .checkpoint}
**Checkpoint:** `uv run main.py` prints your message. You deliberately removed a closing quote, read the error from the bottom, and fixed it.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Forgetting the closing quote or bracket.
- Writing `Print` or `PRINT`. Python cares about upper and lower case: only `print` works.
- Using curly "smart" quotes copied from a document. Use plain `"`.
- Being afraid of errors. They are Python telling you exactly what to fix.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Print your name and your goal on two separate lines, using two `print` calls.
2. Add a comment above each one explaining why you wrote it.
3. Make one mistake on purpose from each row of the error table. Write down the message you got.
4. **Think:** the interpreter runs line by line. If line 3 has an error, did lines 1 and 2 run? Test it.
:::
