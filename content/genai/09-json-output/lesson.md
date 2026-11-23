---
title: JSON output
summary: Make the model answer in JSON your code can read - learn json.loads and json.dumps, JSON mode, cleaning messy replies, and handling bad JSON.
plan_ids: []
---

Until now, the model's answer was text for a human. In real apps your **code** reads the answer. For example: take a support email, and get back the customer name, the product and the mood, as data.

Free text is hard for code to read. **JSON** is easy. So we ask the model for JSON.

## What is JSON?

**JSON** is a plain-text way to write data. It looks like Python dictionaries and lists, with small differences:

```json
{"name": "Dev", "age": 30, "tags": ["python", "ai"], "active": true, "boss": null}
```

- Keys are always in **double quotes**. Single quotes are not valid.
- `true`, `false` and `null` are in lowercase. (Python has `True`, `False` and `None`.)
- No comma after the last item.

## The `json` module

Python has a built-in `json` module. You met modules and imports in Python level 1.

`json.loads(text)` turns JSON **text** into Python data. (Think: "load string".)

```python
import json

data = json.loads('{"name": "Dev", "age": 30, "active": true}')
print(data["name"])      # -> Dev
print(data["active"])    # -> True
print(type(data))        # -> <class 'dict'>
```

`json.dumps(data)` goes the other way: Python data into JSON text. (Think: "dump string".)

```python
print(json.dumps({"name": "Dev", "active": True}))
# -> {"name": "Dev", "active": true}
```

## Bad JSON

If the text is not valid JSON, `json.loads` raises `json.JSONDecodeError`. That is a kind of `ValueError`, so you can catch it with either name.

```python
try:
    json.loads("{'name': 'Dev'}")      # single quotes: not valid
except json.JSONDecodeError:
    print("not valid JSON")            # -> not valid JSON
```

Models write bad JSON sometimes. A real app must **expect** this.

### Step by step: a safe parser

Write `safe_loads(text)`. It returns the data, or `None` if the text is not valid JSON.

1. Put `json.loads(text)` in a `try`.
2. Return its result.
3. In `except json.JSONDecodeError`, return `None`.

```python
def safe_loads(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None

safe_loads('{"a": 1}')    # -> {'a': 1}
safe_loads("hello")       # -> None
```

This is the same try/except pattern you used for `safe_int` in Python level 1. Remember it for the first exercise.

## Asking for JSON

You can ask in the prompt:

```
Reply with JSON only. Use the keys "name" and "age". No other text.
```

This often works. But a model may still add words around the JSON ("Sure! Here is the JSON:"), or wrap it in a code fence:

````
```json
{"name": "Dev"}
```
````

You can fix the most common cases in code (next section). But there is a better, direct way.

## JSON mode

Groq has a setting called **JSON mode**. It makes the model produce valid JSON:

```python
response = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=messages,
    response_format={"type": "json_object"},
)
data = json.loads(response.choices[0].message.content)
```

Rules for JSON mode:

- **Say "JSON" in your messages.** The API needs the word in the prompt, or it returns an error.
- It gives you **valid JSON**, but it does **not** check that the **keys and types** are what you wanted. That check comes in lesson 10.
- If the answer is cut off by `max_completion_tokens`, the JSON can be broken. Give enough room.
- Keep the temperature low.

## JSON schema mode (structured outputs)

JSON mode gives you valid JSON, but the keys can still be wrong. A stronger setting lets you send a **JSON schema**: a description of the exact keys and types you want.

A **schema** is a plan of the shape. It is itself written as a dictionary:

```python
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
    },
    "required": ["name", "age"],
    "additionalProperties": False,
}
```

Read it: the answer is an object with a string `name` and an integer `age`. Both are required. No other keys are allowed.

You send it in `response_format`:

```python
response = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=messages,
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "person", "schema": schema},
    },
)
```

> Not every model supports `json_schema`. Check `console.groq.com/docs/structured-outputs` for the models that do. Use plain JSON mode as the fallback.

Even with a schema, **still validate in code** (lesson 10). A schema reduces the mistakes. It does not remove them.

You will build the schema part in the fourth exercise.

## Cleaning a messy reply

When you cannot use JSON mode, or as extra safety, clean the text before you parse it. A useful trick: the JSON object is **from the first `{` to the last `}`**. Cut out that part.

Steps:

1. Find the first `{` with `text.find("{")`. If there is none, it returns `-1`.
2. Find the last `}` with `text.rfind("}")`.
3. If either is missing, or the `}` comes before the `{`, there is no JSON. Give up.
4. Otherwise take the slice `text[start : end + 1]`. The `+ 1` is needed to include the last `}`.

```python
def cut_braces(text):
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    return text[start : end + 1]

cut_braces('Sure! Here it is: {"a": 1} Hope that helps.')   # -> '{"a": 1}'
cut_braces("no json here")                                    # -> None
```

Then parse the slice with your safe parser.

## The shape of an `ask_json` function

The whole thing, as one function:

1. Build messages. The prompt must say "JSON".
2. Call the model with `response_format={"type": "json_object"}`.
3. Take the text of the reply.
4. Parse it safely. Return the data, or `None` if it is bad.

You will write this in the exercises. The caller then decides what to do with `None`: retry, or show an error. Lesson 10 adds retries and checking.

## Try it live

1. Ask for JSON in plain words, with **no** JSON mode: *"Give me a city and its country as JSON."* Print the raw reply. Does it have extra words or code fences around it? That is why you clean the reply.
2. Add `response_format={"type": "json_object"}` (the prompt must still say "JSON"). Print again. What changed?
3. Parse the reply with `json.loads`. Then ask for a field that does not exist and see what your code does. This is the gap that lesson 10 closes.

## A little deeper

- **Why models break JSON.** They write token by token and sometimes forget to close a bracket, or add a comment, or a trailing comma.
- **Order of keys.** Ask for a `"reasoning"` key *before* the `"answer"` key, and the model thinks first, then answers.
- **Numbers and booleans.** Models often write numbers as strings (`"30"`) or booleans as `"yes"`. You must check types.
- **Streaming JSON** is hard, because the text is not valid until the end. Wait for the whole answer if code reads it.
- **Tool calling** (lesson 11) is another way to get structured data. The arguments of a tool call are JSON too.

## Common mistakes

- Using `json.loads` on a reply without a `try/except`.
- Forgetting the word "JSON" in the messages when using JSON mode.
- Thinking JSON mode checks keys and types. It only guarantees valid JSON.
- Using `end` instead of `end + 1` in the slice, and cutting off the last `}`.
- Writing Python values (`True`, `None`, single quotes) in JSON by hand.
- Using a very small `max_completion_tokens`, so the JSON is cut off.

## Interview corner

**How do you get reliable structured data out of an LLM?**
Ask for JSON, use JSON mode or structured outputs, keep the temperature low, validate with a schema (Pydantic), and retry with the error message when validation fails.

**What does JSON mode guarantee, and what not?**
It guarantees syntactically valid JSON. It does not guarantee the right keys, types or values, and a cut-off answer can still be broken.

**What can go wrong when parsing model output?**
Extra text around the JSON, code fences, trailing commas, single quotes, wrong types, missing keys, and truncated output.

**Difference between `json.loads` and `json.load`?**
`loads` reads from a string. `load` reads from a file object.

## Summary

- `json.loads(text)` gives Python data. `json.dumps(data)` gives text.
- Bad JSON raises `json.JSONDecodeError`. Catch it.
- JSON mode: `response_format={"type": "json_object"}`, and the word "JSON" must be in the messages.
- JSON mode guarantees valid JSON, not the right keys or types.
- Clean messy replies by cutting from the first `{` to the last `}`.
- Reference: `reference/genai-groq.md`.
