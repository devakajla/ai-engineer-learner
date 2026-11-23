---
title: Packaging with uv
summary: Set up a real Python project with uv - virtual environments, pyproject.toml, dependencies, version rules, the lock file and command-line entry points.
plan_ids: [PY-09]
---

Until now you ran single files. A real project has many files and uses **other people's code** (libraries). You need a clean way to say: "this project needs these libraries, in these versions", so it works on your laptop, a teammate's laptop and a server. This is **packaging**.

**uv** is a fast tool that does this. (You have already used `uv run` and `uv add` in this app.)

## The problem: one Python, many projects

Project A needs `requests 2.28`. Project B needs `requests 2.32`. If both install into one place, they fight.

The fix is a **virtual environment** (a "venv"): a private folder with its own Python and its own libraries, for **one project only**. uv makes and uses it for you, in a folder called `.venv`.

## Starting a project

```bash
uv init taskflow          # makes a new folder with a starter project
cd taskflow
```

This creates the main file: **`pyproject.toml`**. It describes your project.

## `pyproject.toml`

TOML is a simple settings format: `[sections]` and `name = value` lines.

```toml
[project]
name = "taskflow"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.110",
    "httpx",
]

[project.scripts]
taskflow = "taskflow.cli:main"

[dependency-groups]
dev = ["pytest>=8"]
```

What each part means:

- `name` and `version`: who the project is.
- `requires-python`: which Python versions can run it.
- `dependencies`: the libraries it needs **to run**.
- `[dependency-groups] dev`: libraries you need only **while developing** (tests, linters). They are not installed on the production server.
- `[project.scripts]`: turns a function into a command (see below).

Python can read TOML with the built-in `tomllib` module:

```python
import tomllib

text = """
[project]
name = "taskflow"
dependencies = ["fastapi>=0.110", "httpx"]
"""
data = tomllib.loads(text)             # text -> dict (like json.loads)
print(data["project"]["name"])         # -> taskflow
print(data["project"]["dependencies"]) # -> ['fastapi>=0.110', 'httpx']
```

`tomllib.loads` reads text. A section like `[project]` becomes a dict inside the dict. A bad file raises `tomllib.TOMLDecodeError`.

### A step-by-step example: read the project name and its libraries

1. Parse the text with `tomllib.loads`.
2. Get the `project` section with `.get`, so a missing section does not crash.
3. Read the fields you need.

```python
def summary(text):
    data = tomllib.loads(text)
    project = data.get("project")
    if project is None:
        raise ValueError("no [project] section")
    return project["name"], len(project.get("dependencies", []))

print(summary(text))     # -> ('taskflow', 2)
```

## The everyday uv commands

| Command | What it does |
|---|---|
| `uv add fastapi` | installs a library and adds it to `dependencies` |
| `uv add --dev pytest` | same, but in the `dev` group |
| `uv remove httpx` | removes it |
| `uv sync` | makes `.venv` match the project files exactly |
| `uv run python main.py` | runs a command inside the project's environment |
| `uv run pytest` | runs your tests the same way |
| `uv lock` | writes or updates the lock file |

You almost never need to "activate" the venv. `uv run` does it for you.

## Version rules

A dependency can carry a **version rule** (called a *specifier*):

| Written | Means |
|---|---|
| `httpx` | any version |
| `httpx==0.27.0` | exactly this version |
| `httpx>=0.27` | this one or newer |
| `httpx>=0.27,<1.0` | newer than 0.27, but below 1.0 (comma means "and") |
| `httpx!=0.28.0` | anything except this one |

Versions look like `1.4.2`: **major.minor.patch** (this is called *semantic versioning*):

- **patch** (`1.4.2` to `1.4.3`): bug fixes only.
- **minor** (`1.4.x` to `1.5.0`): new features that keep old code working.
- **major** (`1.x` to `2.0`): changes that **can break** your code.

That is why people write `>=1.4,<2.0`: "I want the new features and fixes, but not a breaking change".

### Comparing versions: numbers, not text

A trap: compare versions as **numbers**, not as text.

```python
print("1.10.0" > "1.9.0")                 # -> False   text compares letter by letter. Wrong!

def parse_version(text):
    return tuple(int(part) for part in text.split("."))

print(parse_version("1.10.0"))            # -> (1, 10, 0)
print(parse_version("1.10.0") > parse_version("1.9.0"))   # -> True   tuples compare item by item
```

Version `1.10.0` is newer than `1.9.0`. The tuple of ints gets it right, because `10 > 9`.

## The lock file

`pyproject.toml` says what you **accept**: `fastapi>=0.110`. Over time, newer versions come out, and two people could install different ones.

**`uv.lock`** records the **exact** version of every library (and the libraries *they* need), that uv chose. When a teammate runs `uv sync`, they get exactly the same versions.

- Commit `uv.lock` to git.
- Do **not** edit it by hand. uv writes it.
- Do not commit `.venv`. It can be rebuilt any time.

## Your own code as a package

A **module** is one `.py` file. A **package** is a folder of modules with an `__init__.py` file. A common layout:

```
taskflow/
├── pyproject.toml
├── uv.lock
├── src/
│   └── taskflow/
│       ├── __init__.py
│       ├── core.py
│       └── cli.py
└── tests/
    └── test_core.py
```

Putting code in `src/` keeps it separate from your tests and stops you from importing the wrong copy by accident.

Inside the package, you import with the package name: `from taskflow.core import add_task`.

## Making a command: entry points

In `[project.scripts]`, the line `taskflow = "taskflow.cli:main"` means: "make a command called `taskflow` that runs the function `main` in `taskflow/cli.py`".

```python
# src/taskflow/cli.py
import sys

def main():
    print("TaskFlow:", sys.argv[1:])
```

Then:

```bash
uv run taskflow hello      # -> TaskFlow: ['hello']
```

`sys.argv` is the list of words typed on the command line. `sys.argv[0]` is the program name.

A file can also work as a program with the `__main__` check (you saw this in lesson 14): `if __name__ == "__main__": main()`.

## Sharing and building

`uv build` makes files you can upload or install elsewhere: a **wheel** (`.whl`) and a source archive. Most apps (like a FastAPI service) are not uploaded to a public index. They are installed from the lock file, or built into a Docker image with `uv sync`.

## Reading a requirement line

Each item in `dependencies` is a **requirement**: a name, then an optional version rule. To pull them apart, look for where the name ends. A name has letters, digits, `-`, `_` and `.`. The first of the characters `< > = ! ~` starts the rule.

```python
import re

def split_requirement(text):
    match = re.match(r"^([A-Za-z0-9_.\-]+)\s*(.*)$", text.strip())
    return match.group(1), match.group(2)

print(split_requirement("fastapi>=0.110,<1.0"))   # -> ('fastapi', '>=0.110,<1.0')
print(split_requirement("httpx"))                 # -> ('httpx', '')
```

Library names are not case-sensitive, and `-` and `_` mean the same. So `Typing_Extensions` and `typing-extensions` are the same package.

## A little deeper (optional)

- **`~=` (compatible release).** `httpx~=0.27.2` means `>=0.27.2` and `<0.28`. Short and often used.
- **Python versions.** `uv python install 3.12` downloads a Python for you. A `.python-version` file says which one the project uses.
- **`pip`.** The older tool. `uv pip install ...` works the same way, but `uv add` is better because it also updates `pyproject.toml`.
- **Extras.** `httpx[http2]` asks for optional extra features of a library.
- **Environment markers.** `pywin32; sys_platform == "win32"` means "only on Windows".

## Common mistakes

- Installing libraries with a global `pip` and not into the project.
- Not committing `uv.lock`, so the server gets other versions.
- Committing the `.venv` folder.
- Comparing versions as text (`"1.10" < "1.9"`).
- Putting test tools in `dependencies` instead of the `dev` group.
- Pinning everything with `==`, so nothing can be upgraded. Use ranges in `pyproject.toml` and let `uv.lock` pin the exact ones.

## Interview corner

- **Q: What is a virtual environment, and why use one?** A private folder with its own Python and libraries for one project, so projects do not clash.
- **Q: What is the difference between `pyproject.toml` and `uv.lock`?** `pyproject.toml` says which versions you accept. `uv.lock` records the exact versions that were chosen, so every install is the same.
- **Q: What does semantic versioning mean?** `major.minor.patch`. Patch is for fixes, minor is for compatible features, and major can break things.
- **Q: How do you keep test libraries out of production?** Put them in a dev dependency group (`uv add --dev pytest`) and install without it on the server.

## Summary

- A virtual environment keeps each project's libraries apart. uv makes it in `.venv`.
- `pyproject.toml` describes the project: name, Python version, dependencies, dev group, scripts. `tomllib` reads TOML.
- Commands: `uv add`, `uv add --dev`, `uv remove`, `uv sync`, `uv run`, `uv lock`.
- Version rules: `==`, `>=`, `<`, `!=`, joined by commas. Compare versions as tuples of numbers.
- `uv.lock` pins exact versions. Commit it.
- Packages are folders with `__init__.py`. `[project.scripts]` makes a command.
