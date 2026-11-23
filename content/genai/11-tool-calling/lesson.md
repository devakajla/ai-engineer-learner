---
title: Tool / function calling
summary: Let the model ask your code to do things - describe tools, read the model's tool calls, run your functions, and send the results back.
plan_ids: []
---

A model cannot check today's weather. It cannot look in your database, or do exact maths, or call an API. It only writes text.

**Tool calling** (also called **function calling**) fixes this. You tell the model which functions your code has. When the model needs one, it **asks** your code to run it. Your code runs the function and sends the result back. Then the model writes the final answer.

This is the base of every AI **agent**. And it is the main thing that will let DevDocs Copilot look inside API specs later.

## The most important idea

> **The model never runs anything.** It only writes a request that says "please call this function with these values". Your code runs the function.

The flow has five steps:

1. You send the messages **and** a list of tools.
2. The model replies with a **tool call** instead of text: a function name and arguments.
3. Your code runs that function.
4. You send the result back as a message with the role `tool`.
5. The model reads the result and writes the final answer.

## Step 1: describe the tools

A tool is described with a dictionary. It has a name, a description and the **parameters** (the inputs) in JSON schema form:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name, like Delhi"},
                },
                "required": ["city"],
            },
        },
    }
]
```

The model reads the `description` to decide **when** to use the tool, so write it clearly. Types are JSON types: `"string"`, `"integer"`, `"number"`, `"boolean"`.

That is a lot of typing for each tool, so write a helper that builds this dictionary from small pieces.

### Step by step: a schema builder

Build the tool dictionary from a name, a description and a dictionary of parameters, `{param_name: (type, description)}`.

1. Make an empty `properties` dictionary.
2. Loop over the parameters. Unpack each `(type, description)` pair, and add `properties[name] = {"type": ..., "description": ...}`.
3. Return the full dictionary. `required` is the list of all parameter names.

```python
def make_tool(name, description, params):
    properties = {}
    for param, (kind, text) in params.items():
        properties[param] = {"type": kind, "description": text}
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": list(params),
            },
        },
    }

tool = make_tool("add", "Add two numbers.", {"a": ("number", "First"), "b": ("number", "Second")})
print(tool["function"]["parameters"]["required"])   # -> ['a', 'b']
```

`list(params)` gives the keys of the dictionary, in order. It is the same pattern you need for the first exercise.

## Step 2: send the tools

```python
response = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)
message = response.choices[0].message
```

`tool_choice="auto"` lets the model decide. The model may answer in text, or ask for tools.

## Step 3: read the tool calls

If the model wants a tool, `message.tool_calls` is a list. If it does not, it is `None`.

```python
for call in message.tool_calls:
    print(call.id)                  # -> call_abc123
    print(call.function.name)       # -> get_weather
    print(call.function.arguments)  # -> '{"city": "Delhi"}'
```

Look at `arguments`. It is a **string** that holds JSON. You must parse it with `json.loads` (lesson 9). And since models write bad JSON sometimes, parse with care.

```python
import json

args = json.loads(call.function.arguments)
print(args["city"])    # -> Delhi
```

The model can ask for **several** tool calls at once (for example, the weather in two cities). So always loop.

## Several tool calls in one reply (parallel calls)

Ask: "What is the weather in Paris and in Delhi?" The model may ask for **two** tool calls in **one** reply: one per city. This is called **parallel tool calls**. `message.tool_calls` is a list, so it can hold many calls.

Your code must **loop** over all of them. Run each one, and send **one `tool` message per call**, each with its own `tool_call_id`. If you answer only the first, the API gives an error, or the model gets confused.

```python
for call in message.tool_calls:
    ...   # run it, make one tool message for it
```

The calls are independent of each other, so they can even run at the same time. You will loop over them in the third exercise.

## Step 4: run the function and answer

Keep your real functions in a dictionary, by name:

```python
def get_weather(city):
    return f"Sunny, 30 C in {city}"      # a real one would call a weather API

functions = {"get_weather": get_weather}
```

To run a call:

1. Look up the function by name: `functions[name]`.
2. Parse the arguments.
3. Call it with `**args`.
4. Make a message with the result.

The result message has the role `tool`. It must carry the **`tool_call_id`**, so the model knows which call this answers. The content must be a **string**:

```python
{"role": "tool", "tool_call_id": call.id, "content": "Sunny, 30 C in Delhi"}
```

What if the model asks for a tool that does not exist? Do not crash. Send back an error text, so the model can recover:

```python
def run_call(name, args, functions):
    if name not in functions:
        return f"error: unknown tool {name}"
    return str(functions[name](**args))

run_call("get_weather", {"city": "Delhi"}, functions)   # -> 'Sunny, 30 C in Delhi'
run_call("fly", {}, functions)                          # -> 'error: unknown tool fly'
```

(`str(...)` makes sure the content is text, even if your function returns a number.)

## Step 5: send everything back

Now call the model a second time. The messages must have the full story:

1. The original messages.
2. The **assistant message** that holds the tool calls.
3. One `tool` message per call.

```python
assistant_message = {
    "role": "assistant",
    "content": message.content,
    "tool_calls": [
        {
            "id": call.id,
            "type": "function",
            "function": {"name": call.function.name, "arguments": call.function.arguments},
        }
        for call in message.tool_calls
    ],
}
messages = messages + [assistant_message] + tool_messages
final = client.chat.completions.create(model=..., messages=messages, tools=tools)
print(final.choices[0].message.content)   # -> It is sunny and 30 C in Delhi.
```

The model now reads the tool result and writes a normal answer.

> Why is the assistant message needed? Remember, the model has no memory (lesson 4). It must *see* that it asked for the tool, and then see the result.

## The whole flow as a function

`chat_with_tools(client, messages, tools, functions)`:

1. Call the model with the tools.
2. If `message.tool_calls` is empty, return `message.content`.
3. Otherwise build the assistant message and run each call into a `tool` message.
4. Call the model again with the longer list, and return its text.

This does **one round** of tools. In Level 5 you will make it a loop: the model may ask for tools again and again, until it is done. That loop is what we call an agent.

## Try it live

1. Write a tool `add(a, b)` with a schema. Ask the model *"What is 1234 + 8765?"*. Print `message.tool_calls`. You will see the request, not the answer.
2. Run the function yourself and send the `tool` message. Print the final answer.
3. Ask a question that needs no tool (*"Say hello"*). What is `message.tool_calls` now? Then give two tools and ask a question for each in one sentence, and look for parallel calls.

## A little deeper

- **Always validate arguments.** The model is a stranger sending you data. Check types, ranges and required keys before you run something. Pydantic (lesson 10) is perfect for this.
- **Safety.** A tool that deletes or spends money needs extra care: limits, allow-lists, and a human confirmation. Never run model-written code or SQL without checks.
- **Errors are information.** If a tool fails, send the error text as the tool result. The model often fixes its own call.
- **`tool_choice` options.** `"auto"`, `"none"` (no tools this turn), `"required"` (must call a tool), or force one specific function by name.
- **Not all models are equal.** Small models can pick the wrong tool or write bad arguments. Test with your model. Groq lists which models support tools and parallel calls in its docs.
- **MCP.** The Model Context Protocol is a standard way to offer tools to models from separate servers. It is the same idea at a larger scale.
- **Token cost.** Tool descriptions are part of the input on every call. Many tools means more tokens.

## Common mistakes

- Thinking the model runs the function.
- Forgetting `json.loads` on `arguments`. It is a string.
- Sending the tool result without the `tool_call_id`.
- Sending a non-string `content` in the tool message.
- Forgetting to add the assistant message with the tool calls before the tool messages.
- Crashing when the model asks for an unknown tool.
- Assuming `tool_calls` always exists. It is `None` when the model answers directly.

## Interview corner

**How does tool calling work?**
You describe functions as JSON schemas. The model replies with a tool call (name and JSON arguments). Your code runs the function and sends the result back as a `tool` message. The model then writes the final answer.

**Who executes the tool: the model or your code?**
Your code. The model only produces the request.

**What do you do if the model passes bad arguments?**
Validate them. If they are invalid, return the error text as the tool result, so the model can correct itself. Do not run the function.

**What is the difference between tool calling and JSON mode?**
JSON mode makes the reply itself JSON. Tool calling lets the model pick among functions and fill in their arguments, so your code can act.

## Summary

- Tools are described as `{"type": "function", "function": {name, description, parameters}}`.
- Send `tools=...` in the call. The model may reply with `message.tool_calls` (a list, or `None`).
- Each call has `id`, `function.name` and `function.arguments` (a JSON **string**).
- Your code runs the function and answers with `{"role": "tool", "tool_call_id": id, "content": text}`.
- Send the assistant message with the tool calls, plus the tool messages, and call the model again.
- Handle unknown tools and bad arguments without crashing.
- Project: step 6 gives Copilot tools to look inside an OpenAPI spec.
- Reference: `reference/genai-groq.md`.
