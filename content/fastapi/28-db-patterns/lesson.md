---
title: "Database patterns: transactions, many-to-many, locking"
summary: Keep data correct with transactions, link tables for many-to-many, optimistic locking for two editors, soft delete, and clean handling of unique-key errors.
plan_ids: [SQL-04, SQL-05, BE-01]
---

You can now create tables, query them with SQLAlchemy and change them with migrations. This lesson adds the patterns that keep data **correct** when real users use your API at the same time:

- Money must not vanish if the server fails half way (**transactions**).
- A student joins many courses and a course has many students (**many-to-many**).
- Two people edit the same record (**optimistic locking**).
- A user deletes something, and you may need it back (**soft delete**).
- A user signs up with an email that exists (**unique errors**).

All examples use plain SQLAlchemy with an in-memory SQLite database, so you can run them.

## Transactions: all or nothing

A **transaction** is a group of database changes that succeed together or fail together.

The classic example is a bank transfer. Move 30 from account A to account B. That is two changes: A loses 30, B gains 30. If the program stops between them, 30 is gone. A transaction prevents this.

```python
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

class Base(DeclarativeBase):
    pass

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(String(50))
    balance: Mapped[int] = mapped_column(default=0)

engine = create_engine("sqlite://")
Base.metadata.create_all(engine)

with Session(engine) as s:
    s.add_all([Account(owner="a", balance=100), Account(owner="b", balance=0)])
    s.commit()

def move(s, src, dst, amount, crash=False):
    try:
        s.get(Account, src).balance -= amount
        if crash:
            raise RuntimeError("server crashed")
        s.get(Account, dst).balance += amount
        s.commit()                      # both changes become permanent together
    except Exception:
        s.rollback()                    # both changes are thrown away
        raise

with Session(engine) as s:
    try:
        move(s, 1, 2, 30, crash=True)
    except RuntimeError:
        pass
    print(s.get(Account, 1).balance, s.get(Account, 2).balance)   # -> 100 0
    move(s, 1, 2, 30)
    print(s.get(Account, 1).balance, s.get(Account, 2).balance)   # -> 70 30
```

- Changes made through a `Session` are not final until `commit()`.
- `rollback()` undoes everything since the last commit.
- The `try / except / rollback / raise` shape is the standard way to keep a transaction safe.

This is the **A** in **ACID** from lesson 9: Atomicity.

### Where does the commit go?

You have layers (lesson 6): route, service, repository. The **service** knows the whole business step, so the **service** decides where the transaction starts and ends.

```python
class TransferService:
    def __init__(self, accounts):          # accounts = a repository
        self.accounts = accounts

    def transfer(self, src, dst, amount):
        self.accounts.take(src, amount)     # repository methods do NOT commit
        self.accounts.give(dst, amount)
        self.accounts.commit()              # one commit for the whole step
```

If each repository method committed by itself, a failure after `take` would leave the money half moved. Rule: **repositories change data, services commit**. This idea is also called a **unit of work**: one business step is one transaction.

A dependency with `yield` (lesson 8) can do this for you for each request: commit if the route worked, roll back if it raised.

```python
def get_db():
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
```

## Worked example: a safe change in one transaction

Exercise 1 is a money transfer. Here is the same pattern for a different problem: **buy a ticket**. A ticket purchase changes two tables: the event has fewer seats, and a purchase row is added. Both must happen, or none.

Rules for `buy(session, event_id, buyer)`:

- No such event: `LookupError`.
- No seats left: `SoldOut` (our own error).
- Otherwise: seats go down by 1, a `Purchase` row is added, commit.
- On any failure nothing is changed.

**Step 1.** The models.

```python
from sqlalchemy import ForeignKey, String, update

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    seats: Mapped[int]

class Purchase(Base):
    __tablename__ = "purchases"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    buyer: Mapped[str] = mapped_column(String(50))

class SoldOut(Exception):
    pass
```

**Step 2.** Start with the checks that need no change. Put **everything** inside `try`.

```python
def buy(session, event_id, buyer):
    try:
        if session.get(Event, event_id) is None:
            raise LookupError("no such event")
```

**Step 3.** Take the seat with **one** `UPDATE` that also checks there is a seat. If no row changed, there was no seat.

```python
        taken = session.execute(
            update(Event).where(Event.id == event_id, Event.seats > 0).values(seats=Event.seats - 1)
        )
        if taken.rowcount == 0:
            raise SoldOut("no seats left")
```

Why one statement? If you read `seats` in Python and then write it back, another request can slip in between, and two people get the last seat. In one `UPDATE ... WHERE seats > 0`, the database does the check and the change as a single step.

**Step 4.** Add the second change, then commit once.

```python
        session.add(Purchase(event_id=event_id, buyer=buyer))
        session.commit()
    except Exception:
        session.rollback()
        raise
```

**Step 5.** Try it.

```python
Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add(Event(id=1, seats=1))
    s.commit()
    buy(s, 1, "ann")
    try:
        buy(s, 1, "bob")
    except SoldOut as e:
        print("bob:", e)                              # -> bob: no seats left
    print(s.get(Event, 1).seats, s.query(Purchase).count())   # -> 0 1
```

One seat, one purchase, and the failed attempt left no trace.

## Many-to-many

Some relationships are **many to many**: a student joins many courses, and a course has many students. You cannot put this in one column. You need a third table, a **link table** (also called an association table), with one row for each pair.

```text
students            enrollments                courses
id | name           student_id | course_id      id | title
1  | Ann            1          | 1              1  | Python
2  | Bob            1          | 2              2  | SQL
                    2          | 1
```

Ann is in Python and SQL. Python has Ann and Bob.

In SQLAlchemy you define the link table, then use `relationship(secondary=...)`:

```python
from sqlalchemy import Column, Table
from sqlalchemy.orm import relationship

enrollments = Table(
    "enrollments",
    Base.metadata,
    Column("student_id", ForeignKey("students.id"), primary_key=True),
    Column("course_id", ForeignKey("courses.id"), primary_key=True),
)

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    courses: Mapped[list["Course"]] = relationship(secondary=enrollments, back_populates="students")

class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    students: Mapped[list[Student]] = relationship(secondary=enrollments, back_populates="courses")
```

- Both foreign keys together are the **primary key**. So the same pair cannot be stored twice.
- `secondary=enrollments` tells SQLAlchemy which table links the two.
- `back_populates` connects the two sides. When you change one side, the other follows.

```python
Base.metadata.create_all(engine)
with Session(engine) as s:
    ann, python = Student(name="Ann"), Course(title="Python")
    ann.courses.append(python)          # SQLAlchemy writes the row in enrollments
    s.add(ann)
    s.commit()
    print([c.title for c in ann.courses])        # -> ['Python']
    print([st.name for st in python.students])   # -> ['Ann']
```

You never touch the `enrollments` table directly. A list `append` makes the row, and `remove` deletes it.

If the link itself needs data (like the date of joining, or a grade), use a normal **model** for the link table with its own columns, instead of a plain `Table`. This is called an association object.

To count, join the link table. Use `outerjoin` if you also want rows with zero:

```python
from sqlalchemy import func, select

count = func.count(enrollments.c.student_id)
rows = s.execute(
    select(Course.title, count)
    .outerjoin(enrollments, enrollments.c.course_id == Course.id)
    .group_by(Course.id)
)
print(rows.all())   # -> [('Python', 1)]
```

Remember the N+1 problem from lesson 10. Reading `student.courses` for many students one by one makes many queries. Use `selectinload(Student.courses)` to load them in one extra query.

## Two editors: optimistic locking

Ann and Bob both open note 7 (version 3). Ann saves. Then Bob saves. Without protection, Bob **silently overwrites** Ann's change. This is the **lost update** problem.

The fix is a **version number** on the row:

1. When a client reads the row, it also gets the `version`.
2. When it saves, it sends back the version it saw.
3. The `UPDATE` only works if the version is still the same, and it adds 1.

```sql
UPDATE notes SET title = :t, version = version + 1
WHERE id = :id AND version = :seen_version;
```

If the number of changed rows is 0, someone else changed the note first. The server answers **`409 Conflict`** (or `412 Precondition Failed`), and the client must reload and try again.

It is called **optimistic** because nobody is locked out. You hope there is no clash, and you only check at the moment of saving. (A **pessimistic** lock, `SELECT ... FOR UPDATE`, locks the row while you work. It is safer for very busy rows, but others must wait.)

```python
class Note(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    version: Mapped[int] = mapped_column(default=1)

class StaleVersion(Exception):
    pass

def update_title(s, note_id, seen_version, title):
    result = s.execute(
        update(Note)
        .where(Note.id == note_id, Note.version == seen_version)
        .values(title=title, version=Note.version + 1)
    )
    s.commit()
    if result.rowcount == 0:
        raise StaleVersion("the note changed, reload it")

Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add(Note(id=7, title="draft"))
    s.commit()
    update_title(s, 7, 1, "Ann's text")          # works, version is now 2
    try:
        update_title(s, 7, 1, "Bob's text")      # Bob still holds version 1
    except StaleVersion as e:
        print(e)                                  # -> the note changed, reload it
```

In an API, this version often travels in an `ETag` header and `If-Match` (Level 3), or as a `version` field in the body.

## Soft delete

A normal `DELETE` removes the row forever. Often that is not what you want: a user deletes a task by mistake, or the law says you must keep invoices.

A **soft delete** only **marks** the row as deleted, and leaves it in the table:

```python
class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    deleted: Mapped[bool] = mapped_column(default=False)   # or a deleted_at timestamp

def soft_delete(s, task_id):
    task = s.get(Task, task_id)
    if task is None or task.deleted:
        return False
    task.deleted = True
    s.commit()
    return True

def list_tasks(s):
    return list(s.scalars(select(Task).where(Task.deleted.is_(False))))
```

Good: you can restore, and keep history.

Bad: **every** query must remember `deleted = false`. One forgotten filter leaks deleted data. A `deleted_at` timestamp is even better than a bool, because it also tells you when. Also think about unique rules: a deleted user's email still blocks a new signup with the same email, unless the unique rule ignores deleted rows.

## Unique errors become `409`

A `UNIQUE` constraint (lesson 9) protects the database from duplicates. When you insert a duplicate, the database raises an error, and SQLAlchemy shows it as `IntegrityError`.

Do **not** check "does the email exist?" first and then insert. Two requests at the same moment can both pass the check. Let the **database** decide, and handle the error:

```python
from sqlalchemy.exc import IntegrityError

class ConflictError(Exception):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)

def signup(s, email):
    try:
        s.add(User(email=email))
        s.commit()
    except IntegrityError:
        s.rollback()                      # the session is unusable until you roll back
        raise ConflictError("email already used")

Base.metadata.create_all(engine)
with Session(engine) as s:
    signup(s, "a@x.io")
    try:
        signup(s, "a@x.io")
    except ConflictError as e:
        print(e)                          # -> email already used
```

Then the exception handler from lesson 13 turns `ConflictError` into `409`. The service stays free of HTTP. Always `rollback()` after an `IntegrityError`.

## Backend concept: who decides, the app or the database?

Whenever two requests can touch the same row, ask: **"What if they run at the same moment?"** The app cannot see the other request. The database can. So the safest rules live **in the database**:

| Problem | Let the database decide with |
|---|---|
| duplicates | a `UNIQUE` constraint |
| overselling | `UPDATE ... WHERE qty > 0` and check `rowcount` |
| lost update | `UPDATE ... WHERE version = :seen` |
| half-done work | a transaction |
| orphan rows | a foreign key |

Check in Python only for friendly messages. The database enforces the real rule.

## A little deeper (optional)

- **`SELECT ... FOR UPDATE`.** `select(Account).where(...).with_for_update()` locks the rows until the transaction ends (works in PostgreSQL, not in SQLite). Use it when many writers fight for the same row. Always lock rows in the same order, or two transactions can wait for each other forever (a **deadlock**).
- **SQLAlchemy's built-in version column.** `__mapper_args__ = {"version_id_col": version}` makes the ORM add the version check to every `UPDATE` and raise `StaleDataError` for you.
- **Isolation levels.** They decide what one transaction can see of another one's work (lesson 9).
- **Cascade deletes.** `ondelete="CASCADE"` on a foreign key deletes children with the parent. Use it carefully.
- **Savepoints.** `session.begin_nested()` makes a smaller transaction inside a bigger one.

## Common mistakes

- Several commits inside one business step, so a failure leaves half the work done.
- Checking in Python and then writing (read, check, write). Another request can sneak in. Use one `UPDATE ... WHERE` and check `rowcount`.
- "Check if it exists, then insert" instead of a `UNIQUE` constraint and catching `IntegrityError`.
- Forgetting `rollback()` after a database error. The session then refuses to work.
- Soft delete without filtering deleted rows in every query.
- Reading `.courses` for many students in a loop (N+1).

## Interview corner

- **Q: What is a transaction? Where do you commit in a layered app?** A group of changes that succeed or fail as one. The service commits (one business step, one transaction). Repositories do not.
- **Q: How do you stop two requests buying the last item?** One atomic `UPDATE ... SET qty = qty - 1 WHERE qty > 0` and check how many rows changed. Or lock the row with `FOR UPDATE`. A Python `if` is not safe.
- **Q: What is optimistic locking?** A version column. A save only works if the version is unchanged, and it adds 1. On a clash, answer `409` and let the client reload. Nobody is locked out.
- **Q: Optimistic or pessimistic locking?** Optimistic when clashes are rare (most web apps). Pessimistic when clashes are common and a retry is expensive.
- **Q: How do you model many-to-many?** A link table with both foreign keys (as a composite primary key), and `relationship(secondary=...)`. Use an association object if the link has its own data.
- **Q: What is a soft delete, and what is the catch?** Mark rows deleted instead of removing them. Every query must filter them out, and unique rules must ignore them.

## Summary

- A transaction is all or nothing: `commit()` to keep, `rollback()` to undo. Services commit, repositories do not.
- Do the check and the change in **one** SQL statement. Use `rowcount` to see if it worked.
- Many-to-many needs a link table. In SQLAlchemy: `relationship(secondary=...)`.
- Optimistic locking: a `version` column and `WHERE version = :seen`. A clash gives `409`.
- Soft delete marks rows and keeps them. Filter them in every query.
- Let a `UNIQUE` constraint decide. Catch `IntegrityError`, `rollback()`, and raise a domain `ConflictError` (`409`).
