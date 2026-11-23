---
title: "Pydantic validation: validators & unions"
summary: Clean and check data with your own rules (field and model validators), add computed values, and accept different body shapes with discriminated unions.
plan_ids: [FA-01, PY-05]
---

In lesson 4 you used `Field(min_length=1)` and `ge=1` to check data. Those rules are great, but real data needs more:

- Clean the text first: remove spaces, make it lowercase.
- Check a rule that is not just a length or a range: "only letters and digits".
- Check two fields **together**: "the end date must be after the start date".
- Add a value that is **worked out** from other fields, like the number of nights.
- Accept a body that can have **different shapes**, like an email message or an SMS.

Pydantic can do all of this. This lesson shows how, with small examples.

## A custom rule on one field: `field_validator`

A **validator** is a function that Pydantic calls when it builds the model. It receives the value, and it can **change it** or **reject it**.

```python
from pydantic import BaseModel, field_validator

class ContactIn(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def clean_phone(cls, value: str) -> str:
        digits = value.replace(" ", "").replace("-", "")
        if not digits.isdigit():
            raise ValueError("phone may only have digits, spaces and dashes")
        return digits

print(ContactIn(phone="98765 43210").phone)   # -> 9876543210
```

Read it slowly:

- `@field_validator("phone")` says: run this function for the field `phone`.
- `@classmethod` is needed just below it. The first parameter is `cls` (the model class). You do not use it here, but you must write it.
- The function receives the value that already passed the type check. Here it is a `str`.
- **Return** the value you want to keep. It can be a cleaned version of the input.
- To reject a value, **raise `ValueError("a clear message")`**. Do not raise `HTTPException` inside a model. A model knows nothing about HTTP.

What does FastAPI do with the `ValueError`? It sends a `422` with the exact place of the error:

```json
{"detail": [{"type": "value_error", "loc": ["body", "phone"], "msg": "Value error, phone may only have digits, spaces and dashes", "input": "abc"}]}
```

Pydantic puts "Value error, " in front of your message. The `loc` points at the field `phone`.

Two more details:

- The validator runs **after** Pydantic has checked the type. By default it sees a `str` if the field is `str`.
- To check a rule **on the cleaned value**, clean it inside the validator, then check. This way a name like `"  ab  "` is first cut to `"ab"` and only then measured.

## Worked example: clean first, then check

Exercise 1 asks you to clean a username and check a password. Here is the same pattern for a different problem: a **coupon code**.

Goal: `POST /redeem` with `{"code": " save-20 "}`.

- The code is cleaned: no spaces at the ends, upper case.
- After cleaning it must be 4 to 12 characters, and may contain only letters, digits and `-`.
- The answer is `{"code": "SAVE-20"}`.

**Step 1.** Write the model with a field of type `str`.

```python
from fastapi import FastAPI
from pydantic import BaseModel, field_validator

app = FastAPI()

class RedeemIn(BaseModel):
    code: str
```

**Step 2.** Add the validator. First **clean**, then **check**, then **return**.

```python
    @field_validator("code")
    @classmethod
    def clean_code(cls, value: str) -> str:
        value = value.strip().upper()
        if not 4 <= len(value) <= 12:
            raise ValueError("code must be 4 to 12 characters")
        if not all(ch.isalnum() or ch == "-" for ch in value):
            raise ValueError("code may only have letters, digits and -")
        return value
```

`ch.isalnum()` is `True` for a letter or a digit. `all(...)` is `True` only if every character passes.

**Step 3.** Write the route. It already receives the cleaned value.

```python
@app.post("/redeem")
def redeem(payload: RedeemIn):
    return {"code": payload.code}
```

**Step 4.** Try it.

```python
client = TestClient(app)
print(client.post("/redeem", json={"code": " save-20 "}).json())   # -> {'code': 'SAVE-20'}
print(client.post("/redeem", json={"code": "ab"}).status_code)     # -> 422
print(client.post("/redeem", json={"code": "no way!"}).status_code) # -> 422
```

You wrote no `if` in the route. The route can trust the value, because the model checked it first. This is the "validate at the boundary" idea from lesson 3.

## A rule on two fields: `model_validator`

Some rules involve **more than one field**. "The end date must be after the start date" cannot be checked by looking at one field alone.

For this, use a **`model_validator`**. With `mode="after"`, it runs after all the fields are checked, and it sees the whole model as `self`.

```python
from datetime import date
from pydantic import BaseModel, model_validator

class TripIn(BaseModel):
    start: date
    end: date

    @model_validator(mode="after")
    def end_after_start(self):
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self
```

- It is a normal method (no `@classmethod`), and it takes `self`.
- It must **return `self`** at the end.
- A `date` is a Python type for a calendar day. In JSON a date is a text like `"2026-03-01"`, and Pydantic converts it for you.

Because the error belongs to the whole body (not one field), the `loc` is just `["body"]`:

```json
{"detail": [{"type": "value_error", "loc": ["body"], "msg": "Value error, end must be after start", ...}]}
```

A typical use is "two password fields must match", "`min` must not be bigger than `max`", or "at least one of `email` and `phone` is given".

## A value worked out from other fields: `computed_field`

Sometimes the output has a value that is **calculated**. You do not want the client to send it. It should come from the other fields.

```python
from datetime import date
from pydantic import BaseModel, computed_field

class Trip(BaseModel):
    start: date
    end: date

    @computed_field
    @property
    def days(self) -> int:
        return (self.end - self.start).days

trip = Trip(start=date(2026, 3, 1), end=date(2026, 3, 4))
print(trip.model_dump())   # -> {'start': datetime.date(2026, 3, 1), 'end': datetime.date(2026, 3, 4), 'days': 3}
```

- `@property` makes a method that you read like a field: `trip.days`, with no brackets.
- `@computed_field` adds it to the output (`model_dump()` and the JSON response).
- Subtracting two dates gives a `timedelta`. Its `.days` is the number of days.

A common way to use it: write one model for the **input** (`TripIn`), and a second model for the **output** that **inherits** from it and adds the computed field. Use the second one as `response_model`.

```python
class TripOut(TripIn):
    @computed_field
    @property
    def days(self) -> int:
        return (self.end - self.start).days

@app.post("/trips", response_model=TripOut)
def create_trip(payload: TripIn):
    return TripOut(**payload.model_dump())
```

`TripOut(**payload.model_dump())` builds the output model from the input values. The `**` unpacks a dict into named arguments, as you saw in lesson 4.

## Several shapes in one body: `Literal` and discriminated unions

Think of a notification API. The client can send an email, an SMS, or a push message. Each has **different fields**, but all arrive at the same endpoint: `POST /notify`.

First, a `Literal` type says "this field can only be this exact value":

```python
from typing import Literal

class Email(BaseModel):
    channel: Literal["email"]
    to: str
    subject: str

class Sms(BaseModel):
    channel: Literal["sms"]
    phone: str
```

`Literal["email"]` accepts only the text `"email"`. Anything else is an error.

Now take **either** model. A union is written with `|`: `Email | Sms`. Without help, Pydantic tries the models one by one, and the error message can be confusing. A **discriminated union** tells Pydantic which field decides the model:

```python
from typing import Annotated
from pydantic import Field

Message = Annotated[Email | Sms, Field(discriminator="channel")]

@app.post("/notify")
def notify(message: Message):
    if isinstance(message, Email):
        return {"sent_via": "email", "target": message.to}
    return {"sent_via": "sms", "target": message.phone}
```

How it works:

- Pydantic reads `channel` first. `"email"` selects `Email`. `"sms"` selects `Sms`.
- Then it checks that model only. If a field is wrong, the error is about that model.
- An unknown channel (like `"fax"`) is a clear `422`.
- `isinstance(message, Email)` checks which model you got.

```python
client = TestClient(app)
print(client.post("/notify", json={"channel": "sms", "phone": "9876543210"}).json())
# -> {'sent_via': 'sms', 'target': '9876543210'}
print(client.post("/notify", json={"channel": "fax", "phone": "1"}).status_code)   # -> 422
```

This pattern is common in AI backends too, for example when a message can be a `text` part or an `image` part.

## Backend concept: where do the rules live?

You now have three places to put a rule. A good habit is to choose the **simplest** one that works:

| The rule is... | Use |
|---|---|
| a length, range or pattern on one field | `Field(...)` |
| a cleaning step, or a custom check on one field | `field_validator` |
| about two or more fields together | `model_validator` |
| about the **outside world** (is this email already used? does this id exist?) | **not** a validator. Put it in a service (lesson 6), because it needs the database. |

Validators should be **fast, and depend only on the data given to them**. If a validator calls the database, it becomes slow and hard to test.

## A little deeper (optional)

- **`mode="before"`.** A `field_validator("x", mode="before")` runs **before** the type check, and sees the raw input. It is useful when you want to accept messy input, like turning `"1,200"` into `1200` before it is checked as an `int`.
- **Checking several fields at once.** `@field_validator("first", "last")` runs the same function for both fields.
- **Strict mode.** By default Pydantic is "lax" and converts `"5"` to `5`. With `strict=True` on a field or model, that conversion is refused.
- **Errors for list items.** If a validator runs on `list[str]` items, the `loc` includes the index, like `["body", "tags", 2]`.
- **`ValueError` vs `AssertionError`.** Use `ValueError`. It is the normal way to say "this value is wrong".

## Common mistakes

- Raising `HTTPException` inside a validator. Raise `ValueError`.
- Forgetting to **return** the value from a `field_validator`. Then the field becomes `None`.
- Forgetting `@classmethod` under `@field_validator`.
- Forgetting to `return self` in a `model_validator(mode="after")`.
- Calling a database or a web service inside a validator.
- Checking the length **before** cleaning. A value like `"  ab  "` then passes a length rule it should fail (or the other way around).

## Interview corner

- **Q: How do you add a custom rule to a Pydantic model?** Use `@field_validator` for one field and `@model_validator` for rules across fields. Raise `ValueError` for a bad value. FastAPI sends it as a `422`.
- **Q: When is a validator the wrong place for a rule?** When the rule needs the database or another service (for example "email must be unique"). Put it in the service layer, and raise a domain error (`409`).
- **Q: What is a discriminated union and why use it?** A union of models where one field (the discriminator) tells which model to use. It is faster and gives clearer errors than trying every model.
- **Q: What is `computed_field` for?** To add a calculated value (from other fields) to the model's output, without letting the client send it.

## Summary

- `field_validator` cleans or checks one field. Return the value, or raise `ValueError`.
- `model_validator(mode="after")` checks rules across fields. Return `self`.
- `computed_field` on a `@property` adds a worked-out value to the output.
- `Literal` limits a field to exact values. With `Field(discriminator=...)` a union of models picks the right model from one field.
- Keep validators fast and free of database calls. Outside-world rules belong in services.
