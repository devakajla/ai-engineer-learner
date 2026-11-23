---
title: "Level 2 project: one assistant function"
summary: Join everything from Level 2 - stored prompts, examples, structured replies with repair, and tools - into one assistant function.
plan_ids: []
---

In Level 2 you learned four skills, one lesson each:

- **Prompts** that are written well (lesson 7).
- **Templates** that are stored, filled and versioned (lesson 8).
- **Structured replies**: JSON that is checked and repaired (lessons 9 and 10).
- **Tools** that the model can ask your code to run (lesson 11).

Alone, each skill is small. In a real app they work **together**. In this lesson you build one function, `assistant`, that uses them all. This is the same step-by-step build you did at the end of Level 1.

## The plan: three small pieces, then the whole

```
prepare_messages   stored prompt + examples + question  ->  messages list
ask_structured     messages + a Pydantic model          ->  a checked object (with repair)
assistant          picks the right way to answer        ->  text, object, or tool answer
```

Each exercise builds one piece. The next exercise gets the earlier pieces for free, as "given" code in the starter. This is how real projects grow: small tested pieces, then a top function that only joins them.

## Piece 1: prepare the messages

Every call needs a `messages` list. In lesson 8 you stored prompts by name and version. In lesson 7 you wrote examples as `user` and `assistant` turns. Now one function joins them:

```
system   <- the stored prompt, filled with values
...      <- the example turns (optional)
user     <- the real question
```

Let's practise the pattern with a different example: a *mail* function that joins a header, extra lines and a footer.

1. Start the result with the header.
2. Add the extra lines, but treat `None` as "no extra lines".
3. Add the footer last.
4. Return the list.

```python
def make_mail(header, lines, footer):
    result = [header]
    result = result + (lines or [])
    return result + [footer]

make_mail("Hi", ["a", "b"], "Bye")   # -> ['Hi', 'a', 'b', 'Bye']
make_mail("Hi", None, "Bye")         # -> ['Hi', 'Bye']
```

`lines or []` means "use `lines`, or an empty list when it is `None`". It also protects you from a famous Python trap: never write `lines=[]` as a default value. The same empty list is shared by every call. Use `None` and make a fresh list inside.

Piece 1 works the same way, with messages instead of strings.

## Piece 2: one repair loop for any shape

In lesson 10 your repair loop was written for `Ticket`. A **model class** is just a value, so you can pass it into a function like any other value. Then one loop works for any shape:

```python
def check_reply(model_class, text):
    try:
        return model_class.model_validate_json(text), None
    except ValidationError as error:
        return None, str(error)
```

It returns **two** values: the result and the error. One of them is always `None`. This is a common Python style for "worked or not, and why". The caller writes:

```python
result, error = check_reply(Ticket, reply)
if error is None:
    ...   # worked
```

The repair loop then does what you learned in lesson 10: call, check, and on a failure send the bad reply and the error back. Stop after `max_tries`.

## Piece 3: the top function

`assistant` has three ways to answer, and your code chooses:

| You pass | What happens |
| --- | --- |
| nothing extra | one plain call, you get text |
| `model_class` | repair loop, you get a checked object |
| `tools` and `functions` | one round of tool calling, you get text |

Tools and a structured reply do not mix in this simple version. If both are given, that is a mistake in the caller's code. Fail early with a clear error, **before** spending money on a call.

This "choose a path, fail early on bad input" shape is how most real LLM functions look.

## Try it live

Use your real Groq key and run your finished `assistant` three times:

1. A plain question with a stored prompt. Change `values` and watch the answer change.
2. The same ticket text with `model_class=Ticket`. Print the object. Try a messy text, like "uhh the login thing is broke!!! asap".
3. A tool question (a small `add` tool). Print the second call's messages and find the `tool` message.

Count the calls each way uses. A plain call uses 1. A structured call uses 1 or more. A tool question uses 2.

## A little deeper

- **Why not one giant function?** Small pieces are easy to test with a fake client. A giant function is hard to test and hard to change.
- **Choose the path from the data.** Here you pass `tools` or `model_class`. Bigger systems use a **router**: another small model call picks the path (lesson 33 touched on this).
- **Cost.** A repair adds a call. A tool question always uses two. Log how many calls each path uses.
- **Combining tools and structure.** You can let the model use tools and then ask for a structured final answer. It means two steps: run the tool round, then a repair loop on the last answer. It is a good extension.
- **Prompt in the registry.** Keeping prompts in a registry means you can change a prompt without changing code, and roll back to an older version.

## Common mistakes

- Using `examples=[]` as a default value. Use `None`.
- Writing a separate repair loop for each model class.
- Making the call first and checking the arguments later.
- Changing the `messages` list that the caller passed in.
- Testing only the path that works, and not the error path.

## Interview corner

**How do you structure the code of an LLM feature so that it is testable?**
Small functions that take the client as an argument: build the messages, call, parse, validate. A fake client lets you test every path with no network.

**Why pass a Pydantic model class into a function?**
So one generic repair loop can serve every output shape. The class is the schema and the checker in one.

**When should the code fail before calling the model?**
When the input is invalid or the request is contradictory. Every call costs money and time.

**What is the difference between a workflow and an agent?**
In a workflow your code picks the steps. In an agent the model picks the next step. `assistant` is a workflow: your code chooses the path. Level 5 builds an agent.

## Summary

- `prepare_messages` joins a stored prompt, examples and a question.
- `ask_structured` is one repair loop for any Pydantic model.
- `assistant` chooses the path (plain, structured or tools) and fails early on a bad mix.
- Build small, test each piece, then join them.
- Use `None` for optional lists, never `[]`.
- Reference: `reference/genai-groq.md`.
