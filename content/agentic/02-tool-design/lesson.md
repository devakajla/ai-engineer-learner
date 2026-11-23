---
title: Designing tools an agent can use
summary: Write tool names, descriptions and parameters that a model uses correctly, return short helpful results, and handle bad calls with clear error texts.
plan_ids: []
---

An agent is only as good as its tools. You can have the best model and the best loop, and still get a bad agent, because the tools were confusing. In practice, **most agent bugs are tool design bugs**: the model picked the wrong tool, sent wrong arguments, or got a 40,000-character answer it could not use.

In GenAI lesson 11 you learned how to *describe* and *run* a tool. This lesson is about making tools **good**.

## The reader of your tool is a model

A normal function has a human reader. They can see the code, ask a colleague, and read the docs. The model has **only** the name, the description and the parameter descriptions. That is the whole manual. Imagine handing a new colleague a tool with this note and nothing else:

```
name: proc
description: processes data
parameters: d (string)
```

They would not know what to do. The model is in the same position. It guesses. Now compare:

```
name: search_orders
description: Find a customer's orders by email address. Use this when the user asks
             about an order, a delivery, or a refund. Returns at most 5 orders, newest first.
parameters: email (string): the customer's email address, like ana@example.com
```

Now it is clear **what** the tool does, **when** to use it, and **what comes back**.

## Ten rules for good tools

### 1. One clear job per tool

A tool that does five things (`manage_orders` with an `action` argument) is harder to use than five tools with clear names. But do not go too far: 40 tiny tools confuse the model too. Aim for **a handful** of tools (about 3 to 10) per agent.

### 2. A name that says the action

Use a verb and a noun, in `snake_case`: `search_orders`, `get_weather`, `create_ticket`. Avoid vague names (`process`, `handle`, `run`) and names that look alike (`get_user`, `fetch_user`, `find_user`). Lowercase letters, digits and underscores are the safest characters. Many APIs reject other characters.

### 3. A description that says WHAT, WHEN and WHAT BACK

Write two or three short sentences:

1. What the tool does.
2. When to use it (and when **not** to, if another tool is close).
3. What it returns, and its limits.

The model decides from this text alone. If two descriptions overlap, the model picks at random.

### 4. Few, simple parameters

Every extra parameter is another chance to get it wrong. Prefer simple types (`string`, `integer`, `boolean`). Give a **short description with an example** for each. For a fixed set of values, use an `enum` so the model cannot invent one:

```python
"sort": {"type": "string", "enum": ["newest", "oldest"], "description": "Order of the results"}
```

### 5. Make mistakes hard

Design the tool so that the wrong call is difficult. For example: take `order_id` as a string like `"A-1042"` (not "the order I mentioned"). Require a full path, not a relative one. Ask for an email address, not "the user". Real engineers call this **poka-yoke** (mistake-proofing).

### 6. Return small, useful results

A tool result goes into the history, and the history is sent on **every** later step. A huge result costs money again and again and can push the important text out of the context window (GenAI lesson 2).

- Return only the fields the model needs, not the whole database row.
- Limit lists (`at most 5 results`) and say so in the description.
- When something is too long, **cut it and say so** (a "truncated" note), so the model can ask for more.
- Use plain readable text or small JSON with clear names.

### 7. Error messages that teach

When a call fails, the model reads the error text and tries again. A good error says **what went wrong** and **what would work**:

```
Bad:   error
Good:  error: unknown tool sub. Available tools: add, div
Good:  error: missing required argument email; argument limit must be integer
```

Never raise an exception out of a tool call into your loop. Catch it, and return the text (GenAI lesson 27).

### 8. Validate every argument

The model is a stranger that sends you data. Check the names, the types and the ranges **before** you run the function. This also protects you: a tool that builds a SQL query or a file path from model text is a security risk (GenAI lesson 30).

### 9. Separate read tools from write tools

Reading (search, get, list) is safe to repeat. Writing (create, send, delete, pay) changes the world. Give write tools extra care: ask a human to approve, make them **idempotent** (running the same call twice has the same effect as once, for example by passing a request id), and keep their power small.

### 10. Test the tools with the model

Write 10 to 20 test questions. Run the agent. Read the traces: which tool did it choose? Were the arguments right? When the model goes wrong, fix the **tool description first**, not the system prompt. Then run the tests again.

## Worked examples for the exercises

You will build four small helpers. Each one is a piece of a safe tool door.

### Step by step: check a description (exercise 1)

Let's practise the shape of the first exercise with a different example: check a recipe card. A good card has a lowercase title with no spaces, a note of at least 15 characters, and each ingredient needs an amount. The function returns a **list of problem texts**, and `[]` means good. Problems are added in a fixed order.

1. Start with an empty list `problems`.
2. For each rule, if it is broken, `append` a text.
3. Return the list.

```python
def check_card(card):
    problems = []
    title = card.get("title", "")
    if not title or " " in title or title != title.lower():
        problems.append("title must be lowercase with no spaces")
    if len(card.get("note", "").strip()) < 15:
        problems.append("note is too short (under 15 characters)")
    for ingredient, amount in card.get("ingredients", {}).items():
        if not amount:
            problems.append(f"ingredient {ingredient} has no amount")
    return problems

card = {"title": "Pasta Bake", "note": "Easy", "ingredients": {"pasta": "200g", "cheese": ""}}
print(check_card(card))
# -> ['title must be lowercase with no spaces', 'note is too short (under 15 characters)', 'ingredient cheese has no amount']
```

`card.get("note", "")` means "the note, or an empty text if it is missing". That keeps the function from crashing on an incomplete card.

### Step by step: check the arguments (exercise 2)

Let's practise the shape of the second exercise with a different example: check an order for a shop. It must have `item` (text) and `count` (a whole number). Other keys are unknown. Missing keys are reported first, then each given key is checked in order.

1. For each required key, if it is not in the data, add "missing" text.
2. For each given key: unknown keys get an "unknown" text. Known keys get a type check.
3. Remember that `True` counts as an `int` in Python, so refuse booleans for numbers.

```python
RULES = {"item": "string", "count": "integer"}

def check_order(order):
    problems = []
    for key in RULES:
        if key not in order:
            problems.append(f"missing required key {key}")
    for key, value in order.items():
        if key not in RULES:
            problems.append(f"unknown key {key}")
        elif RULES[key] == "string" and not isinstance(value, str):
            problems.append(f"key {key} must be string")
        elif RULES[key] == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
            problems.append(f"key {key} must be integer")
    return problems

print(check_order({"item": "pen", "count": 3}))       # -> []
print(check_order({"count": True, "color": "red"}))   # -> ['missing required key item', 'key count must be integer', 'unknown key color']
```

`isinstance(value, int)` asks "is this value an int?". `isinstance(True, int)` is `True` (a `bool` is a kind of `int`), so a separate `isinstance(value, bool)` check is needed.

### Step by step: cut a long result (exercise 3)

Let's practise the shape of the third exercise with a different example: shorten a message for a small phone screen, and tell the reader how much was hidden.

1. If the text fits, return it unchanged.
2. Otherwise keep the first part with a slice `text[:limit]`.
3. Add a note with the number of hidden characters.

```python
def shorten(text, limit):
    if len(text) <= limit:
        return text
    hidden = len(text) - limit
    return text[:limit] + f" ... ({hidden} more)"

print(shorten("Hello", 10))                  # -> Hello
print(shorten("Hello there my friend", 5))   # -> Hello ... (16 more)
```

### Step by step: one safe door (exercise 4)

Let's practise the shape of the fourth exercise with a different example: a coffee machine that has a few buttons. A press on an unknown button gets a helpful message. A broken button gets an error text. A good press returns the result. The function **never crashes**.

1. Unknown button: tell what the buttons are.
2. Try the action inside `try` / `except Exception`.
3. Return a text for every outcome.

```python
def press(buttons, name):
    if name not in buttons:
        return f"error: unknown button {name}. Available buttons: " + ", ".join(sorted(buttons))
    try:
        return str(buttons[name]())
    except Exception as error:
        return f"error: {type(error).__name__}: {error}"

def make_tea():
    return "tea ready"

def make_soup():
    raise RuntimeError("no water")

buttons = {"tea": make_tea, "soup": make_soup}
print(press(buttons, "tea"))     # -> tea ready
print(press(buttons, "pizza"))   # -> error: unknown button pizza. Available buttons: soup, tea
print(press(buttons, "soup"))    # -> error: RuntimeError: no water
```

In your exercise this function also validates the arguments and cuts long results, using the helpers from the earlier exercises.

## Try it live

Make two tools with **overlapping** descriptions, for example `search_docs` ("searches documents") and `find_pages` ("finds pages"). Give the agent from GenAI lesson 27 five questions.

1. Print which tool it chose for each question. Does it pick the right one?
2. Rewrite the two descriptions so that each says **when to use it**. Run the five questions again. Did the choices improve?
3. Make a tool that returns a very long text. Watch how the tokens per step grow (`response.usage`). Add `truncate_result` and compare.
4. Send a wrong argument on purpose (a string where an integer is needed) and read the error text that your door sends back. Does the model fix its next call?

## A little deeper

- **Token cost of tools.** All tool descriptions are sent on every call. 30 long descriptions can cost thousands of tokens per step. Keep them short and few. Some systems load tools on demand.
- **Tool results are untrusted input.** A web page returned by a tool can contain "ignore your instructions". Treat tool output as data (GenAI lesson 37).
- **Pagination.** For long lists, return a page plus a `next_page` value, and let the model ask for the next page.
- **Return ids.** Return the id of every object (`order_id`), so the next tool call can use it exactly.
- **Natural names beat codes.** `"status": "shipped"` is easier for a model than `"status": 3`.
- **Idempotency keys.** A write tool can take a `request_id`. If the same id arrives twice (because of a retry), do the work only once.
- **Structured outputs.** Newer APIs can force arguments to match a schema. You still need validation: it is your safety net on every model.
- **MCP.** The Model Context Protocol is a standard way to offer tools from separate servers. The design rules here apply to those tools too (you will meet MCP in week 8).

## Common mistakes

- A description like "processes data". The model cannot tell when to use it.
- Two tools with almost the same job and almost the same description.
- Too many tools (20 and more) in one agent.
- Returning the whole database row or a whole web page.
- Raising exceptions out of a tool, so the whole loop crashes.
- Error messages that say only `error`.
- Not validating arguments, or trusting `True` to be a number.
- Fixing a wrong tool choice in the system prompt instead of in the tool description.
- Write tools with no approval and no limits.

## Interview corner

**What makes a good tool for an LLM agent?**
A clear name with a verb, a description that says what it does, when to use it and what it returns, few simple typed parameters with descriptions (and enums for fixed sets), short results, and error messages that tell the model how to fix the call.

**Why validate tool arguments if the model follows a schema?**
Models still send wrong or missing values, and schemas are not always enforced. Validating protects your code, gives the model a clear error to correct, and blocks unsafe input.

**A model keeps choosing the wrong tool. What do you do?**
Read the traces. Check for overlapping descriptions or too many tools. Make each description say when to use it, merge or remove tools, add an example, then rerun the test questions. Change the tool text before changing the prompt or the model.

**How do you handle very large tool outputs?**
Return only the needed fields, limit and paginate lists, truncate with a clear note, and let the model ask for more. Large results cost tokens on every later step.

**What is an idempotent tool and why does it matter?**
Running it twice has the same effect as once. Retries and repeated model calls happen, so write tools (payments, emails) should use a request id so that a duplicate does not cause a double action.

## Summary

- The model sees only the name, description and parameter descriptions. They are the whole manual.
- Rules: one job per tool, a verb name in `snake_case`, a description of what / when / what back, few simple parameters (use enums), make mistakes hard, small results, teaching errors, validate arguments, separate read and write, test with the model.
- `check_tool_spec` finds weak descriptions. `validate_args` checks names and types (refuse `True` for numbers). `truncate_result` cuts long output with a note. `safe_tool_call` is one door that never crashes and always returns text.
- Fix wrong tool choices in the tool descriptions first.
- Reference: `reference/genai-groq.md`.
