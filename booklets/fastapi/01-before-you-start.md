# 1. Before you start

This booklet is different from a normal reference. You will **build one real project with me, step by step**. By the end you will have written a complete backend, and you will know how to start any new backend project from an empty folder.

## What we build: TaskFlow

TaskFlow is a task manager API. Users sign up, log in and keep their own list of tasks.

@@ flow | Figure 1.1: the whole project at the end of the booklet.
Client|browser, app or curl|blue <-> TaskFlow API|FastAPI;routes, services, repositories|green <-> Database|users and tasks|yellow
@@ end

Why a task manager? It is small enough to finish and big enough to need everything a real backend needs: validation, a database, login, tests, deployment.

## How each chapter is built

Every chapter follows the same pattern, so you always know where you are.

| Part | What it is |
| --- | --- |
| **Idea** | a short plain explanation |
| **Steps** | numbered things you type. Do them, do not only read |
| **Folder now** | a tree that shows how your project looks after the steps |
| **Why here?** | why each file lives in that folder |
| **Checkpoint** | a command to run and the exact result you should see |
| **Common mistakes** | the traps |
| **Interview corner and exercises** | quick practice |

> **Type the code yourself.** Copy-paste teaches your fingers nothing. If your result is different from the checkpoint, stop and fix it before moving on. The next step depends on it.

## What you need

- A terminal (Terminal on Mac, any terminal on Linux, WSL on Windows).
- **Python 3.12 or newer**: `python3 --version`.
- **uv**, a fast tool that manages Python projects and packages. Install: `curl -LsSf https://astral.sh/uv/install.sh | sh` (see docs.astral.sh/uv).
- A code editor (VS Code is fine).
- `curl` to call your API from the terminal.

## The big idea of folder structure

Beginners put everything in one file. That works for 50 lines and fails at 500. Experienced developers split the code so that **each file has one job and a clear home**.

Here is the shape we will reach, and *why* it looks like this.

```
taskflow/
├── pyproject.toml          # project info + packages
├── .env                    # secrets and settings (never in git)
├── alembic/                # database migrations
├── app/
│   ├── main.py             # builds the app. The entry point
│   ├── core/               # settings, security, logging, errors
│   ├── db/                 # database engine and session
│   ├── models/             # database tables
│   ├── schemas/            # request and response shapes
│   ├── repositories/       # code that talks to the database
│   ├── services/           # business rules
│   └── api/
│       ├── deps.py         # shared dependencies
│       └── routes/         # URLs (HTTP layer)
└── tests/                  # tests
```

Do not memorise it. We will build it one folder at a time, and each time I will tell you *what made us need it*. That is the best way to learn it.

The one rule behind the whole tree:

> **A request flows down through the layers, and each layer only talks to the one below it:** `route -> service -> repository -> database`.

@@ stack | Figure 1.2: the flow of a request through your folders.
api/routes|receive the HTTP request, return the HTTP response|blue
services|decide what is allowed and what happens|green
repositories|read and write the database|yellow
models + db|tables and connection|gray
@@ end

## Five rules for deciding where code goes

Whenever you are not sure where a piece of code belongs, ask these questions, in order.

1. Does it use `Request`, status codes or `HTTPException`? It belongs in **routes**.
2. Does it describe the shape of data coming in or going out? It belongs in **schemas**.
3. Does it make a decision ("is this allowed?", "is stock enough?")? It belongs in **services**.
4. Does it run SQL or use the session? It belongs in **repositories**.
5. Is it used by everything (settings, password hashing, logging)? It belongs in **core**.

Keep this list. In chapter 6 you will use it for real.

## Before chapter 2

Check your tools:

```bash
python3 --version
# -> Python 3.12.x (or newer)
uv --version
# -> uv 0.x.x
```

::: {.box .interview}
**Interview corner**

**Q: Why not put all the code in `main.py`?**
It becomes hard to read, test and change. Splitting by job lets you change one part without breaking others, and lets several people work at once.

**Q: What is the role of each layer?**
Routes handle HTTP, services hold the rules, repositories handle the database.
:::

::: {.box .exercise}
**Exercises**

1. Name the three things a request passes through in our layers, in order.
2. Where would you put: (a) a function that checks a password is strong enough, (b) the SQL that finds a task by id, (c) the code that returns `404`?
3. Install `uv` and check that `uv --version` works.

*Answers are at the end of the booklet.*
:::
