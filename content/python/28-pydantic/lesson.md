---
title: Pydantic
summary: Check and clean data with Pydantic - field rules, validators, aliases, computed fields, strict mode, generic models and TypeAdapter.
plan_ids: [PY-05]
---

**Pydantic** is a library that turns messy outside data (JSON from an API, a web form, an AI answer) into clean Python objects. It reads your **type hints** (lesson 27) and checks every value. If something is wrong, it raises a clear error. FastAPI uses Pydantic for every request and response.

This lesson uses the Pydantic v2 names. Install it with `uv add pydantic`.

## A model: a class with checked fields

Make a class that inherits from `BaseModel`. Each field is a type hint. Pydantic checks the data when you create the object, and **converts** values where it can (for example the text `"12.5"` becomes the number `12.5`).

```python
from pydantic import BaseModel, Field, ValidationError

class Product(BaseModel):
    name: str = Field(min_length=1)       # at least 1 character
    price: float = Field(gt=0)            # greater than 0
    tags: list[str] = []                  # optional, empty by default

p = Product.model_validate({"name": "Pen", "price": "12.5"})
print(p.price)       # -> 12.5      the text was converted
print(p)             # -> name='Pen' price=12.5 tags=[]
```

`Product(name="Pen", price=12.5)` works too. `model_validate(...)` takes a dict.

`Field(...)` adds simple rules. Common ones:

| Rule | Meaning |
|---|---|
| `gt=0`, `ge=0` | greater than, greater than or equal |
| `lt=10`, `le=10` | less than, less than or equal |
| `min_length=3`, `max_length=20` | length of a string or list |
| `pattern=r"^\w+$"` | the text must match this pattern (`\w` means a letter, digit or `_`) |
| `default=None` | the value if none is given |

When the data is wrong, you get a `ValidationError` that lists **every** problem:

```python
try:
    Product(name="", price=-1)
except ValidationError as e:
    print(e.error_count())                 # -> 2
    print(e.errors()[0]["loc"])            # -> ('name',)
    print(e.errors()[0]["type"])           # -> string_too_short
```

After a `Product` exists, every field is valid. The rest of your code can trust it.

### Optional fields

A field that may be missing or `None`: `age: int | None = None` (lesson 27). If it is given, the rules still apply:

```python
class Person(BaseModel):
    age: int | None = Field(default=None, ge=13)

print(Person().age)         # -> None
print(Person(age=20).age)   # -> 20
# Person(age=5) raises ValidationError
```

## Field validators: your own rules for one field

When `Field(...)` cannot express a rule, write a function and mark it with `@field_validator("field_name")`. Put `@classmethod` under it (lesson 19), because the function belongs to the class.

The function receives the value and must do one of two things:

- **Raise `ValueError`** if the value is bad. Pydantic turns it into a validation error.
- **Return** the value (it may change it, for example make it lowercase).

```python
from pydantic import field_validator

class User(BaseModel):
    username: str
    email: str

    @field_validator("username")
    @classmethod
    def clean_username(cls, v):
        if " " in v:
            raise ValueError("must not contain spaces")
        return v.lower()            # return the changed value

    @field_validator("email")
    @classmethod
    def clean_email(cls, v):
        return v.strip().lower()

u = User(username="DEV", email="  Dev@X.io ")
print(u.username, u.email)          # -> dev dev@x.io
```

> **Always `return` the value.** If you forget, the field becomes `None`.

A step-by-step example: a model with a `code` that must be 4 letters and is stored in uppercase.

1. Use `Field(min_length=4, max_length=4)` for the length.
2. Write a `@field_validator("code")` that checks `v.isalpha()` (only letters), and raises `ValueError` if not.
3. Return `v.upper()`.

```python
class Ticket(BaseModel):
    code: str = Field(min_length=4, max_length=4)

    @field_validator("code")
    @classmethod
    def letters_only(cls, v):
        if not v.isalpha():
            raise ValueError("code must contain only letters")
        return v.upper()

print(Ticket(code="abcd").code)     # -> ABCD
```

Field validators run **after** the `Field` rules and the type check. So inside the validator, `v` already has the right type and length.

To check something like a password, you can use `re.search` (the `re` module, lesson 25) or simple string tests such as `any(ch.isdigit() for ch in v)`.

## Model validators: rules across fields

A rule that needs **two or more fields** (like "the two passwords match") cannot go in a field validator. Use `@model_validator(mode="after")`. It runs after the whole model is built, and receives `self`. It must **return `self`**.

```python
from datetime import date
from pydantic import model_validator

class DateRange(BaseModel):
    start: date
    end: date

    @model_validator(mode="after")
    def check_order(self):
        if self.end < self.start:
            raise ValueError("end must not be before start")
        return self

print(DateRange(start="2026-01-01", end="2026-02-01").end)    # -> 2026-02-01
```

(`"2026-01-01"` was converted into a real `date`.)

## Aliases: other names for the outside world

Outside APIs often use `camelCase` (`orderId`), but Python code uses `snake_case` (`order_id`). An **alias** is the name used outside. An **alias generator** makes the aliases for you:

```python
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

class Order(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    order_id: int
    total_amount: float

o = Order.model_validate({"orderId": 7, "totalAmount": 99.5})   # camelCase in
print(o.order_id)                       # -> 7       snake_case in Python
print(o.model_dump(by_alias=True))      # -> {'orderId': 7, 'totalAmount': 99.5}
print(Order(order_id=8, total_amount=1.0).order_id)             # -> 8
```

- `alias_generator=to_camel` maps `order_id` to `orderId`.
- `populate_by_name=True` also lets you use the Python name (`Order(order_id=8, ...)`).
- `model_dump(by_alias=True)` gives the aliased names back.

If you need the same settings on several models, make a base class with the `model_config`, and inherit from it. (Settings in `model_config` are inherited.) Nested models inside need the same config to read camelCase.

One field can have its own alias: `Field(alias="orderId")`.

## Turning a model back into data

```python
class Item(BaseModel):
    id: int
    name: str
    note: str | None = None
    secret: str = "x"

item = Item(id=1, name="Pen")

print(item.model_dump())                      # -> {'id': 1, 'name': 'Pen', 'note': None, 'secret': 'x'}
print(item.model_dump(exclude_none=True))     # -> {'id': 1, 'name': 'Pen', 'secret': 'x'}
print(item.model_dump(exclude={"secret"}))    # -> {'id': 1, 'name': 'Pen', 'note': None}
print(item.model_dump(include={"id"}))        # -> {'id': 1}
print(item.model_dump_json())                 # -> {"id":1,"name":"Pen","note":null,"secret":"x"}
```

- `exclude_none=True` leaves out values that are `None`.
- `mode="json"` (`model_dump(mode="json")`) makes everything JSON-safe (dates become text).

### `exclude_unset`: only what the client sent

For an update (an HTTP PATCH), you want only the fields the client **actually sent**, even if one of them is `null`. That is `exclude_unset=True`:

```python
class ItemUpdate(BaseModel):
    name: str | None = None
    note: str | None = None

upd = ItemUpdate.model_validate({"name": None})
print(upd.model_dump())                       # -> {'name': None, 'note': None}
print(upd.model_dump(exclude_none=True))      # -> {}                 the null is lost!
print(upd.model_dump(exclude_unset=True))     # -> {'name': None}     only what was sent
```

## Computed fields: values worked out from other fields

`@computed_field` over a `@property` adds a value that is calculated, and it shows up in `model_dump`:

```python
from pydantic import computed_field

class Cart(BaseModel):
    prices: list[float]

    @computed_field
    @property
    def total(self) -> float:
        return round(sum(self.prices), 2)

print(Cart(prices=[1.5, 2]).model_dump())    # -> {'prices': [1.5, 2.0], 'total': 3.5}
```

The `-> float` return hint is needed. A computed field cannot be given as input. It is only worked out.

## Useful `model_config` options

| Option | What it does |
|---|---|
| `extra="forbid"` | unknown fields are an error (the default `"ignore"` drops them) |
| `str_strip_whitespace=True` | strips spaces from all strings |
| `strict=True` | no conversion: `"5"` is NOT accepted for an `int` |
| `frozen=True` | the object cannot change, and it is hashable |
| `from_attributes=True` | can build the model from an object's attributes (like a database row) |
| `alias_generator`, `populate_by_name` | aliases (above) |

Normally Pydantic is **forgiving**: it converts `"30"` to `30`. With strict mode, it is not:

```python
class Strict(BaseModel):
    model_config = ConfigDict(strict=True)
    age: int

# Strict(age="30") raises ValidationError
print(Strict(age=30).age)    # -> 30
```

## Generic models: `Page[T]`

A model can take a type, like a generic class (lesson 27). The most common use is a page of results:

```python
class Page[T](BaseModel):
    items: list[T]
    total: int

page = Page[Product].model_validate({"items": [{"name": "Pen", "price": 1}], "total": 1})
print(page.items[0].name)    # -> Pen
```

`Page[Product]` checks each item as a `Product`. You can make one inside a generic function too:

```python
def make_page[T](items: list[T]) -> Page[T]:
    return Page[T](items=items, total=len(items))
```

In FastAPI you will write `response_model=Page[TaskRead]`, a documented, typed page of results.

## `TypeAdapter`: validate things that are not models

Sometimes you have a plain **list** of items and no wrapper model. `TypeAdapter` checks any type:

```python
from pydantic import TypeAdapter

adapter = TypeAdapter(list[Product])
products = adapter.validate_python([{"name": "Pen", "price": 1}])
print(products[0].name)                                          # -> Pen

products = adapter.validate_json(b'[{"name": "Ink", "price": 2}]')
print(products[0].price)                                         # -> 2.0
```

`validate_json` takes JSON text (or bytes) directly. That is cleaner than `json.loads` plus a loop. It is great for AI output and third-party JSON.

## A little deeper (optional)

- **Speed.** The Pydantic v2 core is written in Rust. `model_validate_json(raw)` reads and checks the JSON in one pass, which is faster than `json.loads` and then `model_validate`.
- **`mode="before"`.** A `@field_validator("tags", mode="before")` runs **before** the type check. Use it to accept `"a,b,c"` for a list field and split it yourself.
- **Old v1 names.** In old code you may see `.dict()`, `.parse_obj()`, `@validator` and `class Config`. In v2 they are `model_dump`, `model_validate`, `@field_validator` and `model_config`.

## Common mistakes

- Forgetting to `return` the value in a `field_validator`. The field becomes `None`.
- Forgetting `@classmethod` under `@field_validator`.
- Forgetting to `return self` in a `model_validator`.
- Using `model_dump()` and then failing to turn dates into JSON. Use `mode="json"`.
- Surprise conversions (`"1"` becomes `1`). Use `strict=True` where it matters.
- Using `exclude_none` for an update, and losing a field the client really sent as `null`.

## Interview corner

- **Q: How do you check that two fields match (password and confirm)?** With a `@model_validator(mode="after")`.
- **Q: An outside API sends camelCase. How do you map it?** `alias_generator=to_camel` with `populate_by_name=True`, and `model_dump(by_alias=True)` for output.
- **Q: How do you return database objects from FastAPI?** Use a response model with `from_attributes=True`.
- **Q: How do you get only the fields the client sent in a PATCH?** `model_dump(exclude_unset=True)`.
- **Q: Why is Pydantic v2 fast?** Its core is written in Rust, and `model_validate_json` reads and checks in one pass.

## Summary

- A `BaseModel` checks and converts data from its type hints. `Field(...)` adds simple rules.
- `@field_validator` checks or changes one field (raise `ValueError`, then return the value). `@model_validator(mode="after")` checks several fields (return `self`).
- Aliases map outside names to Python names. `model_dump` has `by_alias`, `exclude`, `exclude_none`, `exclude_unset` and `mode="json"`.
- `@computed_field` adds a worked-out value.
- `model_config` options: `extra`, `strict`, `frozen`, `from_attributes`, `str_strip_whitespace`.
- Generic models (`Page[T]`) and `TypeAdapter` check lists and raw JSON.
