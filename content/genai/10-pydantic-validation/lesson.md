---
title: Pydantic validation and retry
summary: Check that the model's JSON has the right keys and types with Pydantic, and when it does not, send the error back to the model and try again.
plan_ids: []
---

In lesson 9 you got valid JSON. But valid JSON can still be **wrong for your code**:

```json
{"title": "Login broken", "priority": "very high"}
```

It parses fine. But your code expects `priority` to be a number from 1 to 5. If you do not check, the bad value travels deep into your app and breaks something far away, which is very hard to debug.

The fix: **validate** right at the door. **Pydantic** is the Python library for this. It is the same library FastAPI uses (you will see it again in the FastAPI track).

## A model is a template with rules

With Pydantic you describe the data you expect, once. You write a **model**:

```python
from pydantic import BaseModel

class Ticket(BaseModel):
    title: str
    priority: int
```

> A note: `class` makes a new kind of object. You will learn classes properly in Python lesson 19. For now, copy this shape: `class Name(BaseModel):`, then one line per field, written as `field_name: type`. That is all you need.

Each line says: this field has this name and this **type**. The `: str` and `: int` are called **type hints**.

Now make a ticket from a dictionary. Use `**data` to spread it into named values (you know this from lesson 5):

```python
data = {"title": "Login broken", "priority": 3}
ticket = Ticket(**data)

print(ticket.title)      # -> Login broken
print(ticket.priority)   # -> 3
```

You read fields with a dot, just like the response object from the API.

## When the data is wrong

Pydantic raises a `ValidationError`:

```python
from pydantic import ValidationError

try:
    Ticket(title="Login broken", priority="very high")
except ValidationError as e:
    print("invalid")   # -> invalid
    print(e)
# 1 validation error for Ticket
# priority
#   Input should be a valid integer, unable to parse string as an integer ...
```

The error message says **which field** is wrong and **why**. This is gold: you can send the message back to the model so it can fix its own mistake. More on that soon.

## Types are converted when it is safe

By default Pydantic is friendly. It converts values when the meaning is clear:

```python
Ticket(title="x", priority="3").priority    # -> 3   (the string "3" became the integer 3)
Ticket(title="x", priority=3.0).priority    # -> 3   (3.0 is a whole number)
```

But it still refuses when the conversion makes no sense: `"very high"`, or `3.5` for an int. This is useful with LLMs, which often write `"3"` instead of `3`.

## More rules with `Field`

A type is not always enough. `priority` must be 1 to 5. Use `Field`:

```python
from pydantic import BaseModel, Field

class Ticket(BaseModel):
    title: str = Field(min_length=1)
    priority: int = Field(ge=1, le=5)
```

`ge` means "greater than or equal". `le` means "less than or equal". Others: `gt`, `lt`, `max_length`.

## Defaults and optional fields

A field with `= value` is **optional**. If it is missing, the default is used.

```python
class Ticket(BaseModel):
    title: str
    priority: int = 3
    tags: list[str] = []

t = Ticket(title="x")
print(t.priority, t.tags)    # -> 3 []
```

`list[str]` means "a list of strings". Pydantic checks every item. Here `[]` is safe: each ticket gets its **own** new list (in plain Python a mutable default like this would be shared, but Pydantic copies it).

## A fixed set of values: `Literal`

If a field may only be one of a few words, use `Literal`:

```python
from typing import Literal
from pydantic import BaseModel

class Review(BaseModel):
    mood: Literal["happy", "sad", "neutral"]

Review(mood="happy")     # ok
Review(mood="angry")     # ValidationError
```

This is the classifier from lesson 7, made exact.

## Parse JSON straight into a model

Pydantic can read JSON text itself. One call does `json.loads` **and** the check:

```python
text = '{"title": "Login broken", "priority": 2}'
ticket = Ticket.model_validate_json(text)
print(ticket.priority)   # -> 2
```

If the text is **not valid JSON**, you get a `ValidationError` too (not a `JSONDecodeError`). So one `except ValidationError` covers both bad JSON and bad fields.

### Step by step: parse or `None`

Write `parse_ticket(text)`. It returns a ticket, or `None` when the reply is no good.

1. Put `Ticket.model_validate_json(text)` in a `try`.
2. Return the ticket.
3. In `except ValidationError`, return `None`.

```python
from pydantic import ValidationError

def parse_ticket(text):
    try:
        return Ticket.model_validate_json(text)
    except ValidationError:
        return None

parse_ticket('{"title": "a", "priority": 2}')    # -> Ticket(title='a', priority=2, tags=[])
parse_ticket('{"title": "a", "priority": "x"}')  # -> None
parse_ticket("hello")                            # -> None
```

It is the same try/except pattern again, with a new error type.

Going the other way: `ticket.model_dump()` gives a plain dictionary, and `ticket.model_dump_json()` gives JSON text.

## Tell the model the shape

A model can also describe itself. `Ticket.model_json_schema()` gives a **JSON schema**: a standard description of the fields and rules. You can paste it into the prompt, so the prompt and the check always match:

```python
import json

schema = Ticket.model_json_schema()
print(list(schema["properties"]))      # -> ['title', 'priority', 'tags']
prompt = "Reply with JSON that follows this schema:\n" + json.dumps(schema)
```

## Retry with the error message

Now the big idea of this lesson. When validation fails:

1. Do not crash.
2. Add the model's bad reply to the messages, as an `assistant` message.
3. Add a `user` message that includes the **error text** and says "fix it".
4. Call again. The model sees its own mistake and corrects it.
5. Stop after a few tries. Do not loop forever.

Here is the loop for a different shape: a mood. The loop calls a function `call_the_model(messages)` that returns the reply text.

```python
class Review(BaseModel):
    mood: Literal["happy", "sad", "neutral"]

def ask_mood(messages, max_tries=3):
    for attempt in range(max_tries):
        reply = call_the_model(messages)
        try:
            return Review.model_validate_json(reply)
        except ValidationError as error:
            messages = messages + [
                {"role": "assistant", "content": reply},
                {"role": "user", "content": f"Your reply was invalid: {error}\nFix it and reply with JSON only."},
            ]
    raise ValueError("could not get a valid review")
```

Read the loop: try, return on success, on failure make a **new** longer list and go round again. After the last try, fail clearly. You write the `Ticket` version in the third exercise.

This is a **repair loop**. It fixes most bad replies in one extra call. It is the standard trick behind libraries such as `instructor`, and you just understood it.

## Try it live

1. Make a `Ticket` model. Ask your model to turn *"the login page crashes, fix asap"* into a ticket as JSON. Validate it with `model_validate_json`.
2. Change the model so `priority` must be 1 to 5. Ask for a priority of "very urgent" in the prompt, and see if the model breaks your rule.
3. Print the `ValidationError` text. Then feed it back to the model as in the repair loop. Count how many calls it took.

## A little deeper

- **Strict mode.** `Ticket.model_validate(data, strict=True)` turns off conversions, so `"3"` is rejected for an int. Use it when you need exactness.
- **`model_validate` vs `Model(**data)`.** Both validate. `model_validate(data)` takes the dictionary directly, which reads nicer.
- **Extra keys.** By default, keys that are not in the model are ignored. Set `model_config = {"extra": "forbid"}` to reject them.
- **Custom checks.** `@field_validator` lets you add your own rules, like "title must not end with a dot". FastAPI lesson 25 covers this.
- **`e.errors()`** gives the problems as a list of dictionaries (`loc`, `msg`, `type`). Use it when you want to show errors in your own format.
- **Cost of retries.** Each repair call costs tokens and time. Cap the tries (2 or 3) and log how often a repair is needed. If it is often, improve the prompt.
- **Native structured outputs.** When the provider enforces a schema for you, repairs are rarer. Keep the validation anyway: it is your safety net, and it works with every model.
- **Where it shows up later.** FastAPI uses Pydantic for request and response bodies. Tool calling (lesson 11) uses the same idea for tool arguments.

## Common mistakes

- Trusting JSON from the model without validating it.
- Catching `JSONDecodeError` only, when you used `model_validate_json` (it raises `ValidationError`).
- A retry loop with no limit.
- Retrying with the same messages. The model needs to see its mistake.
- Forgetting that `Ticket(**data)` needs all required fields.
- Expecting `"3"` to be rejected for an int. By default it is converted.

## Interview corner

**Why validate LLM output with Pydantic?**
JSON mode only guarantees syntax. Pydantic checks the keys, types and ranges, so wrong data is caught at the boundary and does not break the app later.

**How do you handle invalid structured output?**
Catch the validation error, send the error message back to the model along with its bad reply, ask for a fix, and retry a limited number of times. Then fail clearly.

**What is the difference between lax and strict validation?**
Lax mode converts compatible values (`"3"` to `3`). Strict mode rejects them.

**How can the prompt and the validation stay in sync?**
Generate the schema from the model with `model_json_schema()` and put it in the prompt.

## Summary

- A Pydantic model lists the fields and types you expect. `Ticket(**data)` checks them.
- Bad data raises `ValidationError`. Its message says which field and why.
- `Field(ge=1, le=5)`, defaults, `list[str]` and `Literal` add rules.
- `Model.model_validate_json(text)` parses and checks in one call. Bad JSON is also a `ValidationError`.
- `model_dump()` gives a dictionary. `model_json_schema()` gives the schema for your prompt.
- Repair loop: add the bad reply and the error to the messages, ask for a fix, retry a few times.
- Project: step 5 gives Copilot answers with a fixed shape: answer, found, confidence and quote.
- Reference: `reference/genai-groq.md`.
