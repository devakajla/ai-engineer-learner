---
title: Files & pathlib
summary: Read and write text files safely with with-open, work with paths using pathlib, and handle JSON and CSV basics.
plan_ids: []
---

Programs often need to keep data: settings, logs, exports. Python reads and writes files with `open`. A tool called `pathlib` helps you work with file paths and folders in a clean way.

## Write and read a text file

```python
with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("first line\n")
    f.write("second line\n")

with open("notes.txt", encoding="utf-8") as f:
    text = f.read()
print(text)
# -> first line
# -> second line
```

What happens here:

- `open(path, mode)` opens a file. `"w"` means write.
- `with ... as f:` gives you the open file as `f`, and **closes it for you** at the end. This is safe even if an error happens inside. Always use `with`. (You will learn how `with` works in Level 2.)
- `f.write(text)` writes text. It does **not** add a new line. Add `"\n"` yourself.
- `f.read()` reads the whole file as one string.

> Always write `encoding="utf-8"` for text files. Without it, the result can depend on the computer.

### Modes

| Mode | Meaning |
|---|---|
| `"r"` | read (the default). The file must exist. |
| `"w"` | write. It **erases** the old content. |
| `"a"` | append: add to the end. |
| `"x"` | create a new file. Error if it exists. |
| `"b"` | binary. Add it to another mode: `"rb"`, `"wb"`. |

## Writing many lines

Here is a step-by-step example. Write every string of a list as its own line:

1. Open the file with `"w"`, inside `with`.
2. Loop over the strings.
3. Write each one followed by `"\n"`.

```python
names = ["Ada", "Linus"]
with open("names.txt", "w", encoding="utf-8") as f:
    for name in names:
        f.write(name + "\n")
# the file now contains: "Ada\nLinus\n"
```

If the list is empty, the loop never runs, and the file is empty.

## Reading in different ways

```python
with open("notes.txt", encoding="utf-8") as f:
    first = f.readline()      # -> 'first line\n'    one line
    rest = f.readlines()      # -> ['second line\n'] all the other lines, as a list

with open("notes.txt", encoding="utf-8") as f:
    for line in f:            # one line at a time (best for big files)
        print(line.strip())   # strip() removes the \n at the end
# -> first line
# -> second line
```

Looping over `f` reads one line at a time, so even a huge file does not fill your memory. `f.read()` and `f.readlines()` load everything at once.

Empty and blank lines: `line.strip()` is `""` (falsy) for a line with only spaces or only `\n`. So `if line.strip():` is true only for lines that have some text:

```python
count = 0
with open("notes.txt", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            count += 1
print(count)    # -> 2   (blank lines are not counted)
```

## `pathlib`: paths as objects

`Path` from `pathlib` stands for a file or folder path. The `/` sign joins the parts and works on every computer.

```python
from pathlib import Path

p = Path("data") / "users.txt"
p.name         # -> 'users.txt'
p.stem         # -> 'users'        the name without the ending
p.suffix       # -> '.txt'         the ending
p.parent       # -> PosixPath('data')
p.exists()     # -> True or False
```

For a name with two dots, `suffix` is the last ending and `stem` is everything before it: `Path("report.final.csv")` has the suffix `.csv` and the stem `report.final`.

A `Path` can read and write directly:

```python
note = Path("note.txt")
note.write_text("hello\n", encoding="utf-8")
print(note.read_text(encoding="utf-8"))   # -> hello

folder = Path("out")
folder.mkdir(exist_ok=True)               # make a folder (no error if it exists)
for f in Path(".").glob("*.py"):          # find files by a pattern
    print(f.name)
```

Other handy things: `Path.home()` (your home folder), `Path.cwd()` (the current folder), `p.is_file()`, `p.is_dir()`, `p.unlink()` (delete a file) and `p.iterdir()` (list a folder).

> Prefer `pathlib` over joining strings like `"data" + "/" + "users.txt"`.

## JSON

JSON is a text format that most web APIs and settings files use. It looks like a Python dict or list. The `json` module changes between JSON text and Python values:

```python
import json

data = {"name": "Dev", "skills": ["python", "sql"], "active": True}

text = json.dumps(data, indent=2)     # Python value -> JSON text
back = json.loads(text)               # JSON text -> Python value
print(back["skills"][0])              # -> python

Path("data.json").write_text(text, encoding="utf-8")
loaded = json.loads(Path("data.json").read_text(encoding="utf-8"))
```

How the types match:

| JSON | Python |
|---|---|
| object | `dict` |
| array | `list` |
| string | `str` |
| number | `int` / `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

For open files there are also `json.dump(obj, f)` and `json.load(f)` (no `s`).

### Merging settings with defaults

A common job is to read settings from a file, with default values for anything the file does not set. Copy the defaults first, so the original is not changed. Then `update` with the file's values:

```python
defaults = {"port": 8000, "debug": False}
settings = dict(defaults)            # a copy
settings.update({"port": 9000})      # the file's values win
print(settings)    # -> {'port': 9000, 'debug': False}
print(defaults)    # -> {'port': 8000, 'debug': False}   unchanged
```

## CSV

CSV is a simple table format. Each line is a row, with commas between the values.

```python
import csv

rows = [{"name": "Ada", "age": 36}, {"name": "Linus", "age": 55}]

with open("people.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age"])
    writer.writeheader()
    writer.writerows(rows)

with open("people.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(row["name"], row["age"])
# -> Ada 36
# -> Linus 55
```

CSV gives you every value as a **string**. Change it yourself: `int(row["age"])`.

## When a file is missing

`open("missing.txt")` raises a `FileNotFoundError`. You will learn how to handle errors in the next lesson. For now, check first:

```python
if Path("missing.txt").exists():
    print("found")
else:
    print("not there")    # -> not there
```

## A little deeper (optional)

- Opening in `"w"` mode **truncates** the file (empties it) the moment you open it, before you write anything.
- `p.suffix` and `p.stem` only look at the last dot.
- `Path.glob("**/*.py")` searches in all sub-folders.

## Common mistakes

- Opening with `"w"` when you meant `"a"`, and erasing the file.
- Not using `with`, so the file may stay open and the data may not be saved.
- Forgetting `"\n"` when you write lines.
- Forgetting `.strip()` and getting `'\n'` at the end of each line.
- Forgetting `encoding="utf-8"`.
- Reading a huge file with `.read()` instead of looping over its lines.
- Building paths with `+` and `"/"` instead of `Path(...) / ...`.

## Summary

- `with open(path, mode, encoding="utf-8") as f:` closes the file for you.
- Modes: `r`, `w` (erases), `a`, `x`, and `b` for binary.
- Loop over `f` to read line by line. `read()` reads everything at once.
- `pathlib.Path` joins with `/` and has `read_text`, `write_text`, `exists`, `mkdir` and `glob`.
- `json.dumps` and `json.loads` work with strings. `json.dump` and `json.load` work with files. `csv.DictReader` and `csv.DictWriter` work with tables.
