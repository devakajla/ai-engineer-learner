# 7. Structured output: getting JSON you can trust

Your code cannot do much with a paragraph of prose. It needs **data**: a ticket with a title and priority, a list of names, a yes or no. The skill here is making the model return data in a fixed shape, and **never trusting** it blindly.

## The problem

Ask a model for JSON and, most of the time, it gives JSON. But "most of the time" is not enough for software. You will sometimes get:

- extra text around it ("Sure! Here is the JSON: ...")
- a missing field, a wrong type, or a made-up value
- JSON cut off because the token limit was reached

Your code must be ready for all of these.

## Level 1: ask clearly

Describe the shape in the system prompt, with an example, and set a low temperature:

```python
system = (
    "Extract a support ticket from the message. "
    'Reply with JSON only, in this shape: {"title": string, "priority": 1, 2 or 3}. '
    "Priority 3 is most urgent."
)
```

## Level 2: JSON mode

Many APIs have a switch that forces the output to be **valid JSON**:

```python
response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    response_format={"type": "json_object"},
    temperature=0,
)
raw = response.choices[0].message.content
```

JSON mode guarantees valid **syntax** (it parses), but not the right **content**: fields may still be missing or wrong. (Providers also offer *schema-constrained* output, where the output must follow a given JSON schema. Support depends on the model, so check the docs.) With JSON mode you usually still need to say in the prompt that you want JSON.

## Level 3: validate with Pydantic

Treat the model's text as **untrusted input from outside**, like data from a form. Parse and check it with a Pydantic model (Python booklet, chapter 13):

```python
from pydantic import BaseModel, Field, ValidationError

class Ticket(BaseModel):
    title: str
    priority: int = Field(ge=1, le=3)

ticket = Ticket.model_validate_json('{"title": "Login bug", "priority": 2}')
print(ticket)
# -> title='Login bug' priority=2
```

If the data is wrong, you get a precise error instead of a hidden bug later:

```python
try:
    Ticket.model_validate_json('{"title": "Login bug", "priority": 9}')
except ValidationError as error:
    print(error.errors()[0]["loc"], error.errors()[0]["msg"])
# -> ('priority',) Input should be less than or equal to 3
```

## Level 4: the repair loop

When validation fails, you can **tell the model what was wrong and let it try again**. Give it its own bad answer and the error message as new turns. Limit the attempts.

```python
def extract_ticket(client, text, tries=3):
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": text},
    ]
    for attempt in range(tries):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0,
        )
        raw = response.choices[0].message.content
        try:
            return Ticket.model_validate_json(raw)
        except ValidationError as error:
            first = error.errors()[0]
            messages += [
                {"role": "assistant", "content": raw},
                {"role": "user",
                 "content": f"Invalid: {first['loc']} {first['msg']}. Return valid JSON only."},
            ]
    raise ValueError("model did not return valid JSON")
```

We ran this with a fake client that answered `priority: 9` first, and a correct answer second:

```
# result:       title='Login bug' priority=2
# calls made:   2
# 2nd call ended with the message:
#   Invalid: ('priority',) Input should be less than or equal to 3. Return valid JSON only.
```

The flow is: **ask, parse, validate, on failure explain and retry a few times, then give up loudly.**

@@ flow | Figure 7.1: the repair loop.
Ask|JSON mode, temperature 0|blue -> Validate|Pydantic|yellow -> OK|use the object|green
@@ end

@@ flow | Figure 7.2: when validation fails.
Validate fails|collect the error|red -> Tell the model|add its answer and the error|yellow -> Ask again|at most 3 tries|blue -> Give up|raise an error|gray
@@ end

Why `raise` at the end and not return an empty object? A silent fake value is worse than an error, because you will not notice the bad data.

## Tips

- Keep the schema **small and flat**. Deeply nested shapes fail more often.
- Use **enums** for fixed choices: `Literal["billing", "bug", "other"]`. The validator then rejects anything else.
- Describe each field in the prompt (what it means), not only its name.
- A field for "unknown" (`None` or a special value) is better than forcing a made-up answer.
- Make the limit big enough. A cut-off JSON never validates (check `finish_reason`).
- Log the raw text when parsing fails. It is the best debugging data you will get.

## Same idea, other tasks

The pattern is not only for tickets. **Classification** (one of N labels), **extraction** (names, dates, amounts from text), **routing** (which tool or team) and **scoring** (a 1 to 5 grade with a reason) are all "ask for a small, checked, structured answer".

::: {.box .checkpoint}
**Checkpoint:** you can explain the difference between valid JSON and correct JSON, and write the repair loop from memory.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Using `json.loads` and trusting the keys exist.
- Believing JSON mode checks your schema. It only checks syntax.
- An infinite retry loop with no limit.
- Returning a default object when parsing fails.
- Token limit too small, so the JSON is cut in half.
- A high temperature for extraction.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: How do you get reliable structured output from an LLM?** Ask for a schema, use JSON mode or schema-constrained output when available, validate with Pydantic, and retry with the error message a limited number of times.

**Q: JSON mode vs schema-constrained output?** JSON mode guarantees valid JSON syntax. Schema-constrained output also forces the fields and types to match a given schema.

**Q: What do you do when validation fails?** Feed the validation error back to the model and retry a few times, then fail clearly.

**Q: Why validate even when the model is good?** Output is probabilistic. Rare malformed or invalid answers will happen at scale.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write a `Person` model (name, age 0 to 120, email or None) and validate three JSON strings, one of them wrong.
2. Build `classify(client, text)` that returns one of `Literal["billing", "bug", "other"]`, validated.
3. Test `extract_ticket` with a fake client that returns invalid JSON twice, then valid.
4. Test that it raises after `tries` bad answers, and counts the calls.
5. Add a `reason` field and check that missing reasons trigger a retry.
6. **Think:** why is a clear failure better than a default value when the model's answer is invalid?
:::
