---
title: SQLAlchemy 2.0 ORM
summary: Map tables to Python classes, query with select(), use one session per request, and avoid the N+1 problem.
plan_ids: [SQL-08, SQL-09]
---

In the last lesson you wrote raw SQL. That showed you what the database really does. Now you will use an **ORM**, which lets you work with Python classes instead of SQL text.

**ORM** means *Object-Relational Mapper*. It maps a table to a class, and a row to an object. It still sends safe, parameterized SQL underneath.

**SQLAlchemy** is the standard ORM in Python. Version 2.0 has a clean API that works well with type hints. This lesson covers the parts you will use in every FastAPI project.

## The four main pieces

| Piece | What it is |
|---|---|
| **Engine** | holds the database address and a **connection pool**. Create it **once** for the whole app. |
| **Session** | one unit of work. It remembers the objects you load or change, then saves them. Create **one per request**. |
| **Model** | a Python class that maps to a table |
| `select()` | builds a query |

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///./taskflow.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
```

- The **URL** chooses the database. For Postgres it would be `postgresql+psycopg://user:pass@host/db`. The rest of your code stays the same.
- `connect_args={"check_same_thread": False}` is only for SQLite. A web server uses several threads, and this lets them share the connection settings.
- `SessionLocal` is a factory. Each call `SessionLocal()` gives you a new session.

## Declaring a model

A model is a class. Each attribute is a column.

```python
from datetime import datetime
from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(10), default="medium")
    done: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

How to read it:

- `class Base(DeclarativeBase)` is the parent of all your models. Every model inherits from it.
- `__tablename__` is the name of the table.
- `Mapped[int]` says the Python type. The column type is chosen for you, or you can give it, like `String(200)`.
- `Mapped[str | None]` means the column **can be empty** (nullable). Without `| None`, the column is `NOT NULL`.
- `default=` is a value that **Python** fills in when you insert. `server_default=` is filled in by the **database** (for example the current time).
- `index=True` makes an index on that column (lesson 9).

## CRUD with a session

```python
from sqlalchemy import select

with SessionLocal() as session:
    # Create
    task = Task(title="Learn the ORM", priority="high")
    session.add(task)
    session.commit()              # runs the INSERT; task.id is now filled in
    session.refresh(task)         # reload from the database (to get created_at)

    # Read one, by primary key (None if missing)
    task = session.get(Task, 1)

    # Read many
    stmt = select(Task).where(Task.done.is_(False), Task.priority == "high").order_by(Task.id).limit(20)
    tasks = session.scalars(stmt).all()      # a list of Task objects

    # Update: just change the attribute, then commit
    task.done = True
    session.commit()

    # Delete
    session.delete(task)
    session.commit()
```

Important points:

- `with SessionLocal() as session:` closes the session at the end.
- `session.add(...)` only **queues** the change. Nothing is saved until `session.commit()`.
- For an update you do not write SQL. You change the attribute, and the session notices.
- Every value goes to the database as a **bound parameter**, so the ORM protects you from SQL injection.

Useful parts of a query:

- `.where(...)` filters. Give several conditions separated by commas, and they are combined with AND.
- `.order_by(Task.created_at.desc())` sorts.
- `.limit(...)` and `.offset(...)` do paging.
- `Task.title.ilike("%sql%")` is a case-insensitive search.
- `func.count()` counts.

```python
total = session.scalar(select(func.count()).select_from(Task).where(Task.done.is_(False)))
```

`session.scalar(...)` gives one value. `session.scalars(...).all()` gives a list.

## Worked example: a model and CRUD functions

Exercise 1 asks for a model and several functions that use a session. Here is the same pattern for a different problem: **movies**.

Goal:

- A `Movie` model with: `id`, `title` (required), `rating` (a whole number, may be empty), `seen` (bool, default `False`).
- `add_movie(session, title, rating=None)`.
- `unseen(session)` returns movies not seen yet, ordered by title.
- `mark_seen(session, movie_id)` returns `True` if it changed something.
- `count_seen(session)` returns the number of seen movies.

**Step 1.** Write the model. For each column ask: what type, required or not, any default?

```python
class Base(DeclarativeBase):
    pass

class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    rating: Mapped[int | None] = mapped_column()
    seen: Mapped[bool] = mapped_column(Boolean, default=False)
```

**Step 2.** Write `add_movie`: add, commit, refresh, return the object.

```python
def add_movie(session, title, rating=None):
    movie = Movie(title=title, rating=rating)
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie
```

**Step 3.** Write `unseen` with `select`, `where` and `order_by`.

```python
def unseen(session):
    stmt = select(Movie).where(Movie.seen.is_(False)).order_by(Movie.title)
    return list(session.scalars(stmt).all())
```

**Step 4.** Write `mark_seen`. Get the object, check two cases, change it, commit.

```python
def mark_seen(session, movie_id):
    movie = session.get(Movie, movie_id)
    if movie is None or movie.seen:
        return False
    movie.seen = True
    session.commit()
    return True
```

**Step 5.** Write `count_seen` with `func.count()`.

```python
def count_seen(session):
    stmt = select(func.count()).select_from(Movie).where(Movie.seen.is_(True))
    return session.scalar(stmt)
```

**Step 6.** Try it on a temporary in-memory database.

```python
engine = create_engine("sqlite://")
Base.metadata.create_all(engine)

with Session(engine) as s:
    add_movie(s, "Up", 9)
    add_movie(s, "Cars")
    print([m.title for m in unseen(s)])   # -> ['Cars', 'Up']
    print(mark_seen(s, 1))                # -> True
    print(mark_seen(s, 1))                # -> False
    print(count_seen(s))                  # -> 1
```

`Base.metadata.create_all(engine)` makes the tables. `Session(engine)` is another way to open a session. Note that `.is_(False)` is used for comparing with `True`, `False` or `None`.

## One session per request: a `yield` dependency

You learned `yield` dependencies in lesson 8. Here is the database version:

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()          # the connection goes back to the pool

DbSession = Annotated[Session, Depends(get_db)]

@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: DbSession):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

The **engine** lives as long as the app. **Sessions** are cheap, short, and **never shared between requests**.

## Returning ORM objects from FastAPI

Your route returns a `Task` object, not a dict. The response model must be told to read **attributes** instead of dictionary keys:

```python
from pydantic import BaseModel, ConfigDict

class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    done: bool
```

Now `response_model=TaskRead` can convert a `Task`. Always use a response model with ORM objects. If you do not, you may leak columns you did not mean to share.

## Relationships and the N+1 problem

A **relationship** lets you go from one object to related objects: from an author to their books.

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    books: Mapped[list["Book"]] = relationship(back_populates="author")

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["Author"] = relationship(back_populates="books")
```

- `ForeignKey("authors.id")` is the real column in the database.
- `relationship(...)` is the Python shortcut. `back_populates` links the two sides, so `author.books` and `book.author` stay in sync.

By default, a relationship is loaded **lazily**: the query runs the first time you touch it. This causes the famous **N+1 problem**:

```python
authors = session.scalars(select(Author)).all()   # 1 query: all authors
for a in authors:
    print(len(a.books))                           # +1 query for EACH author
```

With 100 authors, that is **101 queries** (1 + N). It is slow, and it is one of the most common ORM performance bugs.

The fix is **eager loading**: tell SQLAlchemy to load the related objects up front.

```python
from sqlalchemy.orm import selectinload

authors = session.scalars(select(Author).options(selectinload(Author.books))).all()
```

Now it takes only **2 queries**, no matter how many authors there are: one for the authors, one for all their books.

Another way is to let the database count, with a single `GROUP BY` query:

```python
stmt = (
    select(Author.name, func.count(Book.id))
    .join(Book, isouter=True)      # a LEFT JOIN: authors with no books stay
    .group_by(Author.id)
    .order_by(Author.name)
)
rows = session.execute(stmt).all()     # a list of (name, count) rows
```

Either way works. `selectinload` is the usual choice for "one parent, many children". `joinedload` uses a JOIN and fits "many children, one parent".

## Creating tables for now

For now, make the tables when the app starts:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)
```

`lifespan` is code that runs once at startup (before `yield`) and once at shutdown (after it). `create_all` only creates **missing** tables. It cannot add a column to a table that already exists. For that, real projects use **migrations**, which is the next lesson.

## Backend concept: connection pooling

Opening a database connection is costly: a network trip, a login, and memory on the database server. A **pool** keeps a few connections open and lends them out.

Settings such as `pool_size` and `max_overflow` limit how many connections one copy of the app can use. This matters, because a database has a hard maximum (Postgres defaults to 100). Many app copies, each with a big pool, can lead to "too many connections" errors.

## A little deeper (optional)

- `autoflush=False` and `expire_on_commit=False` are common session settings. The second one keeps objects readable after `commit()` without another query.
- For tests with an in-memory SQLite database that several threads share, people use `poolclass=StaticPool`, so every thread uses the same single connection.
- **ORM or raw SQL?** Use the ORM for normal CRUD (safe, portable, fast to write). For complicated reports or speed-critical queries, raw SQL is fine.
- You can see the SQL that SQLAlchemy runs with `create_engine(..., echo=True)`. It is a great way to learn, and to spot N+1.

## Common mistakes

- Creating a new engine for each request. No pooling, slow, and the database runs out of connections.
- Sharing one session between requests or threads.
- Forgetting `commit()` (changes vanish) or `refresh()` (database defaults like `created_at` are missing).
- N+1 queries from lazy relationships inside loops or while building the response.
- Writing `Task.done == None` instead of `Task.done.is_(None)`, or using Python `and` / `or` instead of passing several conditions to `.where()`.

## Interview corner

- **Q: Engine vs session?** The engine is for the whole app and owns the pool. A session is for one unit of work. It tracks objects and the transaction.
- **Q: What is the N+1 problem, and how do you fix it?** One query for the parents, plus one query per parent for a relationship. Fix it with eager loading (`selectinload` or `joinedload`) or with a join.
- **Q: How does FastAPI return ORM objects?** Use `response_model` with `from_attributes=True`.
- **Q: ORM or raw SQL?** ORM for most CRUD. Raw SQL or SQLAlchemy Core for complex reports or performance-critical queries.

## Summary

- One engine for the app (it owns the pool). One session per request, from a `yield` dependency.
- Models use `DeclarativeBase`, `Mapped[...]` and `mapped_column(...)`.
- Query with `select(...).where(...).order_by(...).limit(...)`, `session.scalars(...)`, `session.get(...)`.
- Use `from_attributes=True` on response schemas.
- Watch for N+1 and fix it with `selectinload` or a `GROUP BY`.
