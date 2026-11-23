# 8. Tool and function calling

A language model only produces text. It cannot check the weather, read your database or send an email. **Tool calling** lets the model ask **your code** to do things for it. This is the base of every "AI agent".

## The idea

You describe your functions to the model (name, purpose, parameters). When a question needs one, the model does **not** run it. It replies with a **request**: "please call `get_weather` with `city = "Pune"`." Your code runs the function, sends the result back, and the model writes the final answer using it.

**The model decides *what* to call. Your code does the actual calling.** That separation is what keeps you in control.

@@ flow | Figure 8.1: the tool-calling round trip.
You|question + tool descriptions|blue -> Model|replies: call get_weather(Pune)|yellow -> Your code|runs the real function|green -> Model|reads the result;writes the answer|yellow -> User|final text|blue
@@ end

## Step 1: describe the tool

A tool description is a JSON schema. The **description** matters a lot, since it is how the model decides when to use the tool.

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name"}},
            "required": ["city"],
        },
    },
}]
```

And the real function, which is plain Python:

```python
def get_weather(city):
    return {"city": city, "temp_c": 21}     # a real one would call a weather service

TOOLS = {"get_weather": get_weather}        # name -> function
```

## Step 2: the model asks for a call

```python
response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
message = response.choices[0].message
```

If the model wants a tool, `message.tool_calls` is a list. Each item has an `id`, `function.name` and `function.arguments`, which is a **JSON string**, not a dict. If the model needs no tool, `tool_calls` is empty and `message.content` is the answer.

## Step 3: run it and report back

Two messages are added to the history: the model's request (with the same `tool_calls`), and one **`tool` message** per call with the result and the matching `tool_call_id`.

## The full loop

An agent is this loop, repeated until the model stops asking for tools. We ran it against a fake client:

```python
import json

def run_agent(client, question, max_steps=5):
    messages = [{"role": "user", "content": question}]
    for step in range(max_steps):
        response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
        message = response.choices[0].message

        if not message.tool_calls:              # no tool wanted: this is the answer
            return message.content

        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {"id": call.id, "type": "function",
                 "function": {"name": call.function.name, "arguments": call.function.arguments}}
                for call in message.tool_calls
            ],
        })
        for call in message.tool_calls:
            try:
                args = json.loads(call.function.arguments)
                result = TOOLS[call.function.name](**args)
            except Exception as error:
                result = {"error": str(error)}
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            })
    return "stopped: too many steps"
```

The test run, with a fake model that first asked for the weather and then answered:

```
# answer:           It is 21 C in Pune.
# model calls:      2
# roles in 2nd call: ['user', 'assistant', 'tool']
# tool message:     {"city": "Pune", "temp_c": 21}
```

Points in the code that are easy to miss:

- **`max_steps`** is a safety belt. Without it, a model that keeps asking for tools would loop for ever and burn money. When we gave a fake that asked for tools every time, the loop stopped with `stopped: too many steps`.
- Arguments arrive as a **string**, so we `json.loads` them. The model can send bad arguments, so we **catch errors** and send the error back as the tool result. The model can then correct itself, which is better than crashing.
- The `tool` message must carry the same `tool_call_id`. That is how the model matches results to requests.
- Models can ask for **several** tools in one reply (parallel calls). The loop above already handles a list.

## Designing good tools

@@ grid 2 | Figure 8.2: the rules for tools that work.
Clear name and description|the model chooses from these;say when to use it and when not|green
Small, simple parameters|a few strings and numbers;with enums for fixed choices|blue
Useful errors|return what went wrong and how to fix it;not a stack trace|yellow
Safe by design|read-only by default;confirm before anything with side effects|red
@@ end

Safety rules that matter:

- **Never let the model run arbitrary code or SQL** because it asked. Validate arguments like any user input.
- For actions with effects (send money, delete data), require **human approval**, or make the tool idempotent.
- **Check permissions in your code**, per user. The model should not decide who is allowed.
- Return as little data as is needed. Big outputs waste tokens.

## Controlling the choice

The `tool_choice` parameter can force the behaviour: let the model decide (`"auto"`, the default), forbid tools (`"none"`), or require one (for example a specific function). Forcing a tool is also a way to get **structured output**: define a tool whose parameters are your schema, and read its arguments.

## When is a tool better than RAG?

Tools fetch **live or computed** data (the weather, a user's orders, a calculation). RAG (chapter 14) fetches **text** from documents. Many systems use both.

::: {.box .checkpoint}
**Checkpoint:** you can draw the five-step round trip, and explain why the model does not run the function itself.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- No `max_steps`, so a confused model loops for ever.
- Passing the arguments string straight to the function without `json.loads` and validation.
- Crashing on a bad tool call instead of returning the error to the model.
- Vague tool descriptions, so the model picks the wrong tool.
- Tools that can delete or pay with no check.
- Forgetting the `tool_call_id`, or forgetting to append the assistant message that made the call.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: How does function calling work?** You give the model tool schemas. It replies with a tool name and JSON arguments instead of text. Your code runs the function, returns the result as a `tool` message, and the model continues.

**Q: Who executes the function?** Your application, never the model.

**Q: How do you stop an agent loop from running for ever?** A maximum number of steps, a timeout and a cost cap.

**Q: How do you make tool use safe?** Validate arguments, check permissions in code, prefer read-only tools, and ask for approval before actions with side effects.

**Q: Why do descriptions matter?** The model chooses tools by reading them.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Add a second tool `add(a, b)` and test that the loop can call both.
2. Test that a tool raising `ValueError` returns `{"error": ...}` to the model instead of crashing.
3. Add a rule that stops the loop if the same tool is called with the same arguments three times.
4. Write a fake client that asks for two tools in the same reply, and check that both results are appended.
5. Design the schema for a `search_orders(status, limit)` tool with an enum for status.
6. **Think:** why should permission checks be inside your tool code, not in the prompt?
:::
