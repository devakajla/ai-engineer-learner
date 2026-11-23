# 13. Clean layers and patterns

A small app can live in one file. A real app grows, and then code becomes a knot: a route that talks to the database, applies business rules, sends emails and formats JSON, all in 200 lines. Nobody dares to change it.

The cure is **structure**. This chapter shows the shape that most good backends share, and a few small design patterns that come up again and again.

## Separation of concerns

Give each part of the code **one job**. When something changes, you touch one place.

@@ stack | Figure 13.1: layers. Each one calls only the layer below it.
Routes (API layer)|HTTP only: read the request, validate, return the response|blue
Services (business layer)|the rules: "stock must be enough", "no double booking"|green
Repositories (data layer)|queries and saves; the only place that knows SQL|yellow
Database|tables|gray
@@ end

| Layer | Knows about | Must not know about |
| --- | --- | --- |
| Routes | HTTP, status codes, JSON | SQL |
| Services | business rules | HTTP, SQL details |
| Repositories | SQL, the ORM | HTTP, business rules |

Why it helps:

- **Test** the rules without a web server or a real database (replace the repository with a fake).
- **Change** the database without touching rules.
- **Reuse** a service from a route, a worker and a script.

A typical folder layout:

```
app/
  main.py          # creates the app
  core/            # settings, security, logging
  api/routes/      # routes (HTTP)
  schemas/         # request and response shapes (Pydantic)
  services/        # business rules
  repositories/    # database access
  models/          # database tables (SQLAlchemy)
```

## Three kinds of "model"

People mix these up. They are different jobs.

| Name | Job | Example |
| --- | --- | --- |
| **Schema / DTO** | the shape of data going in or out of the API | `UserCreate` (has password), `UserOut` (no password) |
| **Domain / service object** | what the business works with | plain data and rules |
| **ORM model** | a database table as a class | `User` table with `password_hash` |

Keeping API schemas separate from table models stops you from leaking internal fields, and lets each side change on its own.

## SOLID in plain words

Five guidelines for clean classes. You do not need to memorise the names. Understand the ideas.

| Letter | Idea | Plain words |
| --- | --- | --- |
| **S** | Single responsibility | one reason to change |
| **O** | Open / closed | add new behaviour by adding code, not by editing old code |
| **L** | Liskov substitution | a child class must work wherever its parent works |
| **I** | Interface segregation | small, focused interfaces, not one giant one |
| **D** | Dependency inversion | depend on an abstraction, not on a concrete thing |

**Dependency inversion** is the most useful one for backends. Your service should not create its own database connection or email sender. It **receives** them.

```python
class OrderService:
    def __init__(self, repo, emailer):   # given from outside
        self.repo = repo
        self.emailer = emailer
```

In tests you pass fakes. In production you pass the real ones. This is **dependency injection**.

## Design patterns that actually come up

A **design pattern** is a named, tested solution to a problem that keeps coming back.

### Repository

Hide all database code behind a small interface.

```python
class UserRepository:
    def get(self, user_id): ...
    def add(self, user): ...
    def find_by_email(self, email): ...
```

The service says `repo.find_by_email(...)` and never writes SQL.

### Service layer

One class or module per area (`OrderService`) holds the rules and coordinates repositories. The route stays thin.

### Strategy

Several ways to do the same job, chosen at run time. Example: payment by card, by UPI, by wallet. Each is a "strategy" with the same method (`pay`). The service picks one. No giant `if method == ...` chains.

```python
strategies = {"card": CardPay(), "upi": UpiPay()}
strategies[method].pay(amount)
```

### Factory

A function or class that **creates** the right object. Example: `make_llm_client("groq")` returns a Groq client, `make_llm_client("openai")` returns an OpenAI one. Callers do not care which.

### Adapter

Wrap a foreign interface so it looks like yours. Every LLM provider has a different SDK. An adapter gives them the same `chat(messages)` method, so you can swap providers (and add fallbacks) without changing your app.

@@ flow | Figure 13.2: an adapter hides provider differences.
Your code|calls chat(messages)|blue -> Adapter|translates the call|green -> Groq or OpenAI SDK|different formats|yellow
@@ end

### Observer (events)

When something happens, many parts react, without the source knowing them. "Order paid" triggers an email, an invoice and a stats update. In backends this is often done with events and queues (chapter 9).

### Singleton, and why you rarely write one

"One shared instance," such as a database engine or a settings object. In Python, a module-level object or a cached function does this. Avoid hidden global state elsewhere.

## Errors: raise rules, translate at the edge

- Services raise **domain errors**: `OutOfStock`, `NotFound`, `NotAllowed`. They know nothing about HTTP.
- The API layer **translates** them: `OutOfStock` becomes `409`, `NotFound` becomes `404`, `NotAllowed` becomes `403`.

This keeps rules reusable, and your error format consistent in one place.

## Configuration

- Read settings from **environment variables**, not from hard-coded values.
- One typed settings object, loaded once at startup (`pydantic-settings`).
- Different values per environment (dev, test, production), the same code.

## Small design practice: an LRU cache (LLD classic)

Interviewers often ask "design an LRU cache". The idea: a dict for fast lookup plus an order of use. When full, remove the least recently used item.

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = OrderedDict()

    def get(self, key):
        if key not in self.data:
            return None
        self.data.move_to_end(key)          # now the most recent
        return self.data[key]

    def put(self, key, value):
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)   # drop the oldest
```

Both operations are O(1). The System Design booklet has more of these.

::: {.box .fastapi}
**How FastAPI does this**

- Routes live in `api/routes/` as `APIRouter` files and stay thin.
- `Depends` is dependency injection: it gives a route a service, which receives a repository, which receives a database session.
- Pydantic classes are the schemas. SQLAlchemy classes are the models.
- `@app.exception_handler(OutOfStock)` turns a domain error into a `409` in one place.
- `pydantic-settings` holds the configuration.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- A "fat route" that holds SQL, rules and formatting.
- A service that imports `fastapi` or raises `HTTPException`. Now it cannot be reused in a worker.
- Returning ORM objects straight from the API, which leaks fields.
- Too many layers for a tiny app. Structure should grow with the project.
- A pattern used because it sounds clever, not because it solves a problem.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Why separate routes, services and repositories?**
Each has one job, so you can test rules without HTTP or a database, change one layer without breaking others, and reuse services from workers and scripts.

**Q: What is dependency injection?**
Passing the things a class needs (repository, client) from outside instead of creating them inside. It makes testing and swapping easy.

**Q: Explain the repository pattern.**
A class that hides all database access behind simple methods, so the rest of the code does not depend on SQL or the ORM.

**Q: Strategy vs factory?**
Strategy chooses between interchangeable behaviours at run time. Factory creates the right object. They often work together.

**Q: How would you support two LLM providers?**
Define one interface (`chat(messages)`), write an adapter per provider, choose with a factory, and add a fallback.

**Q: Which SOLID principle matters most for testability?**
Dependency inversion: depend on abstractions so you can inject fakes.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Sort these into route, service or repository: (a) check that the user has enough balance, (b) `SELECT * FROM orders WHERE user_id = ?`, (c) return `404` when not found, (d) send a confirmation email.
2. A route function is 150 lines long and contains SQL, an `if` chain of rules and JSON building. Describe how you would split it.
3. Your app must accept payments by card, UPI and wallet, and more later. Which pattern fits and why?
4. Explain why an `OutOfStock` error should not be a `HTTPException`.
5. Sketch an `LLMClient` interface and two adapters (`GroqAdapter`, `OpenAIAdapter`). What does the service call?
6. **Think:** when is a layered structure too much?
:::
