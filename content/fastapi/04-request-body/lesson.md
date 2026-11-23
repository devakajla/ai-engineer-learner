---
title: Request bodies & Pydantic
summary: Accept JSON data safely with Pydantic models, field rules and clear 422 errors.
plan_ids: [FA-01, PY-05]
---

Path and query parameters carry small values, like an id or a filter. To **create** or **update** something, the client has to send a bigger piece of data: a JSON **request body**.

In FastAPI you describe that data once, as a **Pydantic model**. Then you get checking, conversion, docs and editor hints for free.

## What is Pydantic?

**Pydantic** is a library that checks data. You write a class with **typed fields**. When you create an object from it, Pydantic checks the data and converts it if needed.

```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    priority: str = "medium"

t = TaskCreate(title="Write tests")
print(t.title)         # -> Write tests
print(t.model_dump())  # -> {'title': 'Write tests', 'description': None, 'priority': 'medium'}
```

Now give it bad data:

```python
TaskCreate(title="")
# ValidationError: 1 validation error for TaskCreate
# title
#   String should have at least 1 character
```

Things to know:

- `class TaskCreate(BaseModel)` means: this class is a Pydantic model.
- A field **without a default** is **required**. A field with a default (like `priority = "medium"`) is optional.
- `str | None = None` means: a string, or nothing, and `None` if not given.
- `Field(...)` adds rules to a field. The rules are the ones you saw in lesson 3: `min_length`, `max_length`, `ge`, `le`, `gt`, `lt`, `pattern`.
- `model_dump()` turns a model into a plain `dict`.
- `Model.model_validate(some_dict)` goes the other way: dict in, model out (with checking).

Pydantic is also **relaxed by default**. If a field is an `int` and you send the text `"5"`, it converts it to `5` instead of failing. Text like `"abc"` still fails.

```python
class Box(BaseModel):
    size: int

print(Box(size="5").size)   # -> 5
```

## A model as the request body

If a function parameter has a Pydantic model as its type, FastAPI reads it from the **JSON body**:

```python
@app.post("/tasks")
def create_task(payload: TaskCreate):
    return {"received": payload.model_dump()}
```

```bash
curl -X POST localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Write tests", "priority": "high"}'
```

Inside the function, `payload` is already a checked `TaskCreate` object. You use it like this: `payload.title`.

### Where does each parameter come from?

FastAPI decides by the kind of parameter:

| The parameter is... | It comes from |
|---|---|
| a name inside `{...}` in the path | the **path** |
| a simple type (`int`, `str`, `bool`, `Enum`, ...) | the **query** |
| a Pydantic model | the **body** |

So one function can use all three:

```python
@app.put("/tasks/{task_id}")
def replace_task(task_id: int, payload: TaskCreate, notify: bool = False):
    return {"task_id": task_id, "notify": notify, "task": payload.model_dump()}
```

Here `task_id` is from the path, `payload` is from the body, and `notify` is from the query (`?notify=true`).

## Validation errors

If the body is wrong, FastAPI answers `422` and lists **every** problem:

```json
{
  "detail": [
    {"type": "string_too_short", "loc": ["body", "title"], "msg": "String should have at least 1 character", "input": ""},
    {"type": "enum", "loc": ["body", "priority"], "msg": "Input should be 'low', 'medium' or 'high'", "input": "urgent"}
  ]
}
```

`loc` is the exact place of the error. Web forms use it to highlight the right input box.

## Models inside models

A field can be another model, or a list of models. Pydantic checks them all.

```python
class Item(BaseModel):
    name: str
    quantity: int = Field(ge=1)
    unit_price: float = Field(gt=0)

class Order(BaseModel):
    customer: str
    items: list[Item] = Field(min_length=1)   # at least one item
```

For lists, `min_length` means "at least this many items".

If the second item has `quantity: 0`, the error `loc` is `["body", "items", 1, "quantity"]`. The `1` is the position in the list. Positions start at 0, so `1` is the **second** item.

You can compute with the checked data in your route:

```python
@app.post("/orders")
def create_order(order: Order):
    total = sum(i.quantity * i.unit_price for i in order.items)
    return {"count": len(order.items), "total": round(total, 2)}
```

## Strict models

### Refuse unknown fields

By default, extra keys in the JSON are quietly **ignored**. That hides typos, for example `"titel"` instead of `"title"`. To refuse them, add a config line to the model:

```python
from pydantic import ConfigDict

class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
```

Now `{"title": "x", "color": "red"}` gives `422`.

### Clean the input

`str_strip_whitespace=True` removes spaces from the start and end of every text field **before** the rules are checked:

```python
class NameIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1)

print(NameIn(name="  Ana  ").name)   # -> Ana
NameIn(name="   ")                   # error: it becomes "" and fails min_length=1
```

You can put both settings in one `ConfigDict(...)`, separated by a comma.

## Worked example: a model with rules, then a route

Exercise 1 asks for a model with several rules, a route, and an extra `id` in the answer. Here is the same pattern for a different problem: **creating a book**.

Goal:

```text
POST /books {"title": " Dune ", "pages": 412}
-> 200 {"id": 1, "title": "Dune", "pages": 412, "summary": null}

POST /books {"title": "Dune", "pages": 0}               -> 422  (pages must be 1 or more)
POST /books {"title": "Dune", "pages": 5, "price": 9}   -> 422  (unknown field)
```

**Step 1.** Write the model. For each field, ask: what type? required or optional? any rules?

```python
from pydantic import BaseModel, ConfigDict, Field

class BookCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=100)
    pages: int = Field(ge=1)
    summary: str | None = Field(default=None, max_length=300)
```

When a field has both a default and a rule, put the default inside `Field(default=...)`.

**Step 2.** Write the route. The parameter's type is the model, so FastAPI reads the body.

```python
@app.post("/books")
def create_book(payload: BookCreate):
    return {"id": 1, **payload.model_dump()}
```

`{"id": 1, **payload.model_dump()}` builds a new dict: first the `id`, then every field from the model. (`**` unpacks a dict into another.)

**Step 3.** Try the three lines of the goal with `TestClient`.

```python
client = TestClient(app)
r = client.post("/books", json={"title": " Dune ", "pages": 412})
print(r.json())   # -> {'id': 1, 'title': 'Dune', 'pages': 412, 'summary': None}
print(client.post("/books", json={"title": "Dune", "pages": 0}).status_code)   # -> 422
```

`json=...` sends the dict as a JSON body.

## Backend concept: schemas are a contract

The model is your **contract** with the client: it says exactly what the client may send. FastAPI enforces the contract.

In real projects you keep **different models for different jobs**. We call these models *schemas*:

- `TaskCreate`: what a client sends to **create** a task. No `id`, no `done`.
- `TaskUpdate`: what a client sends to **change** a task. Every field is optional.
- `TaskRead`: what the API **sends back**. It includes `id`, `done` and so on.

Never accept fields from the client that only the server should control, such as `id`, `owner_id` or `is_admin`. If you do, a client can set them to anything. This bug has a name: **mass assignment**.

Keep schemas in their own file, for example `app/schemas/task.py`, not inside the route file.

## A little deeper (optional)

- `Field(...)` can also take `description` and `examples`. They appear in `/docs`.
- `model_dump_json()` gives a JSON string instead of a dict.
- A **strict** model refuses conversions: with `strict=True`, `"5"` is not accepted for an `int`.
- A list default like `tags: list[str] = []` is safe in Pydantic, because each object gets its own copy. In a normal function it is **not** safe, so do not copy that habit outside Pydantic.
- Pydantic v2 is fast because its checking core is written in Rust.

## Common mistakes

- Sending JSON with `curl` but forgetting `-H "Content-Type: application/json"`. The server then does not read the body.
- Using one model for both input and output. You may accept or show fields you should not.
- Checking values by hand with `if` inside the route, when a `Field(...)` rule would do it.
- Forgetting that `"   "` (only spaces) passes `min_length=1` unless you also strip spaces.

## Interview corner

- **Q: How does FastAPI know if a parameter comes from the body or the query?** A Pydantic model means body. A name in the path means path. Other simple types mean query. (You can change this with `Body()` or `Query()`.)
- **Q: What is mass assignment and how do you prevent it?** It is when the client can set fields it should not control. Prevent it with separate input schemas that leave those fields out, and optionally `extra="forbid"`.
- **Q: Why is Pydantic v2 faster than v1?** Its checking engine, `pydantic-core`, is written in Rust.

## Summary

- A Pydantic model describes and checks a JSON body. Add rules with `Field(...)`.
- Path name means path, simple type means query, model means body.
- Bad input gives `422` with a precise `loc`.
- Models can contain other models and lists of models.
- `extra="forbid"` refuses unknown fields. `str_strip_whitespace=True` cleans text.
- Keep separate `Create`, `Update` and `Read` schemas, in their own files.
