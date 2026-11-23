# 18. Start a new project from scratch

You built TaskFlow while following steps. Now the real test: build a **new** project **without** a guide. This chapter gives you a recipe you can use for every future project, and a small project to practise it on.

## The recipe: ten steps in a fixed order

@@ vflow | Figure 18.1: the order that avoids rework.
1 Write the idea|what does it do? who uses it? list the nouns and actions|blue -> 2 Design the data|tables, columns, relations, indexes: on paper first|purple -> 3 Design the API|list every route: method, path, status codes|yellow -> 4 Create the skeleton|folders, config, health route, git|green -> 5 Build one slice end to end|model, schema, repo, service, route, test|orange
@@ end

@@ vflow | Figure 18.2: after the first slice works.
6 Add the other slices|one resource at a time, test each|green -> 7 Add auth and ownership|users, login, owner_id on every private table|red -> 8 Add errors, logging, settings|custom errors, handlers, .env|yellow -> 9 Add migrations, Docker, CI|Alembic, Dockerfile, compose, pytest in CI|blue -> 10 Write the README|how to run, env vars, example calls|gray
@@ end

The most important habit is step 5: build **one thin slice all the way through** before building anything wide. A slice that works from route to database proves your structure. Then adding the next resource is just copying the pattern.

## The structure recipe

Every time you create a project, make this skeleton first:

```bash
mkdir bookmarks && cd bookmarks
git init
uv init --bare
uv add "fastapi[standard]" "sqlalchemy[asyncio]" aiosqlite alembic pydantic-settings
uv add --dev pytest pytest-asyncio httpx

mkdir -p app/{core,db,models,schemas,repositories,services,api/routes} tests
touch app/__init__.py app/main.py
touch app/core/{__init__,config,exceptions}.py
touch app/db/{__init__,base,session}.py
touch app/api/{__init__,deps,router}.py app/api/routes/__init__.py
touch tests/{__init__,conftest}.py
touch .env .env.example README.md
printf ".venv/\n__pycache__/\n.env\n*.db\n" > .gitignore
```

Then in this order:

1. `core/config.py`: `Settings` with `database_url` and `secret_key`.
2. `main.py`: `create_app()` and a `/health` route. Run `uv run fastapi dev app/main.py`.
3. `db/base.py`, `db/session.py`.
4. The first model, schemas, repository, service, route, test.
5. `alembic init -t async alembic`, edit `env.py`, first migration.

Do not skip step 2. A running app with `/health` in the first ten minutes means every later problem is a **small** problem.

## The five questions (again)

When you do not know where code goes, ask (from chapter 1):

1. Does it read or write the database? **repository**
2. Is it a business rule? **service**
3. Is it about HTTP (status code, header, parameter)? **route**
4. Is it the shape of data in or out? **schema**
5. Is it settings, security or shared tools? **core**

## Practice project: Bookmarks API

Build it alone. Use TaskFlow as a reference, not as a copy.

**What it does:** a user saves links with tags and notes, and finds them later.

**Data**

| Table | Columns |
| --- | --- |
| `users` | id, email (unique), password_hash, created_at |
| `bookmarks` | id, owner_id (FK, indexed), url, title, note, created_at |
| `tags` | id, name (unique) |
| `bookmark_tags` | bookmark_id, tag_id (many-to-many link table) |

**Routes** (all under `/api/v1`, all private except register and login)

| Method and path | Does | Success | Errors |
| --- | --- | --- | --- |
| `POST /auth/register` | sign up | 201 | 409, 422 |
| `POST /auth/login` | get a token | 200 | 401 |
| `POST /bookmarks` | save a link | 201 | 422 |
| `GET /bookmarks?tag=&q=&limit=&offset=` | list and search my links | 200 | 422 |
| `GET /bookmarks/{id}` | one link | 200 | 404 |
| `PATCH /bookmarks/{id}` | change it | 200 | 404, 422 |
| `DELETE /bookmarks/{id}` | remove it | 204 | 404 |
| `POST /bookmarks/{id}/tags` | add a tag | 200 | 404 |

**Rules to put in the service**

- A user cannot save the same URL twice (`409`).
- A user cannot see another user's links (`404`).
- A tag name is lowercase and has no spaces.
- Maximum 500 bookmarks per user (`409`).

**Stretch goals** (each one uses a chapter): a background job that fetches the page title (12), an `/export` endpoint that streams CSV (13), an upload route for importing a bookmarks file (14), Docker and CI (16).

## Order of work for the practice project

1. Idea and data on paper (steps 1 and 2).
2. The skeleton and `/health` (step 4).
3. **Slice:** register and login. Test them.
4. **Slice:** create and get one bookmark, with ownership. Test it.
5. The rest of the routes, one by one, with a test each.
6. Tags (the many-to-many part: the hardest bit).
7. Migration, then Docker, then CI.

## A review checklist before you call it done

@@ grid 2 | Figure 18.3: finish line.
Structure|routes have no business rules;services have no HTTP;imports go downward only|green
Safety|passwords hashed;secret in env;ownership checked everywhere;inputs validated with max lengths|red
Quality|tests for happy and bad paths;consistent error shape;logging with request id|blue
Delivery|migrations committed;Dockerfile and compose work;README says how to run|yellow
@@ end

## Common mistakes in new projects

::: {.box .mistake}
**Common mistakes**

- Designing every table and route in detail for weeks before running any code. Design the first slice only.
- Building all models first and all routes last. Build vertically, by slice.
- Starting with Docker, auth and a queue on day one. Add them when the base works.
- Copying the whole of TaskFlow and renaming. You learn nothing. Re-type the pattern.
- Not committing often. Commit after every working slice.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: How do you structure a FastAPI project?**
Layers: routes (HTTP), services (business rules), repositories (database), schemas (data shapes), core (settings and security), with dependencies wiring them. Imports go one way, downward.

**Q: How do you start a new API?**
Write down the data and routes, create a small skeleton with a health route, build one thin slice end to end with a test, then repeat per resource and add auth, migrations and Docker.

**Q: Why use an application factory (`create_app`)?**
Settings and overrides can differ per run, tests can build a fresh app, and import time has no side effects.

**Q: How do you keep a project from becoming a mess?**
Clear layers, one rule for where code goes, tests for the important rules, and refactoring when a file grows too big.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Build the Bookmarks API following the order above. Commit after each slice.
2. Write the README: how to install, set `.env`, run migrations, run the server and the tests.
3. Ask someone (or use a clean folder) to follow your README. Where did it fail? Fix it.
4. Add the `max 500 bookmarks` rule using a setting, a custom error and a handler.
5. **Think:** which of the ten steps do beginners skip most, and what does it cost them later?
:::
