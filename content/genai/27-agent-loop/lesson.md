---
title: The agent loop
summary: Build an agent from scratch - a loop where the model asks for tools, your code runs them, and the model decides when it is done - with step limits and loop guards.
plan_ids: []
---

In lesson 11 the model could ask for a tool **once**. You ran it, sent the result, and got the final answer. That is one round.

Real tasks need more than one round. "Find the cheapest of these three flights, then book it" needs a search tool, then maybe a price tool, then a booking tool. The model cannot know in advance how many steps it needs. So you let it **decide**, inside a loop. A program like that is called an **agent**.

## What is an agent?

> An **agent** is a loop. The model looks at the situation, picks an action (a tool call), your code runs it, the result goes back to the model, and this repeats until the model says it is done.

```
question -> [ model decides ] -> tool call -> [ your code runs it ] -> result
                  ^                                                       |
                  |_______________________________________________________|
            (repeat until the model answers without a tool call)
```

Think of a new employee with a phone and a list of numbers. You say "find out why the order is late". They call one number, listen, decide who to call next, and so on, until they can tell you the answer. They decide the steps. You only gave the goal and the tools.

Three words you will hear:

- **Step**: one turn of the loop (one model call plus the tools it asked for).
- **Trajectory** (or **trace**): the full list of steps and results.
- **Stop condition**: the rule that ends the loop.

## The one rule that makes it work

The model has no memory (lesson 4). So every step you send the **whole history again**: the question, every earlier tool request and every tool result. The history is the agent's memory.

That has a cost: each step is longer than the one before, so each step costs more tokens. A 10-step agent costs much more than 10 times one call. Keep this in mind for lesson 29.

## Step 1: keep the model's message in the history

When the model asks for a tool, the SDK gives you an object. To put it in the history you turn it into a plain dictionary. If you forget this, the next call has tool results with no request before them, and the API gives an error or the model gets confused.

Let's practise the shape of this first exercise with a different example: turn a reply object from a shop robot into a dictionary. The dictionary always has `"says"`. It has `"items"` only if the robot is carrying items.

1. Start with the dictionary that always exists.
2. If the object has items (not `None`, not empty), add the key.
3. Return it.

```python
from types import SimpleNamespace

def robot_to_dict(robot):
    result = {"says": robot.says}
    if robot.items:
        result["items"] = [item.upper() for item in robot.items]
    return result

print(robot_to_dict(SimpleNamespace(says="Hi", items=None)))            # -> {'says': 'Hi'}
print(robot_to_dict(SimpleNamespace(says="Here", items=["pen", "ink"])))  # -> {'says': 'Here', 'items': ['PEN', 'INK']}
```

`if robot.items:` is false for `None` and for an empty list, so one check covers both. Your first exercise is this, with the tool calls.

## Step 2: one step of the agent

A step has four parts:

1. Call the model with the messages and the tools.
2. Add the model's message to the history.
3. If it asked for **no** tool, it is done: its text is the answer.
4. Otherwise run every tool it asked for, and add one `tool` message for each.

You make a **new** list each time (`messages + [...]`) instead of changing the old one. This keeps the earlier history safe, and it makes the code easy to test.

```python
def agent_step(client, messages, tools, functions):
    response = client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, tools=tools)
    message = response.choices[0].message
    new_messages = messages + [message_to_dict(message)]
    if not message.tool_calls:
        return {"done": True, "answer": message.content, "messages": new_messages}
    for call in message.tool_calls:
        new_messages = new_messages + [run_tool_call(call, functions)]
    return {"done": False, "answer": None, "messages": new_messages}
```

(`run_tool_call` is from lesson 11. It never crashes: an unknown tool or a failing tool becomes the text `error: ...`, which the model can read and react to.)

## Step 3: the loop

Now call `agent_step` again and again. The loop needs a **limit**, because a model can keep asking for tools forever.

Let's practise the "loop with a limit" shape with a different example: guess a secret number by always trying the middle of a range.

1. Repeat at most `max_steps` times.
2. In each step, do one try. If it is right, return at once.
3. If the loop ends without success, return a "gave up" result.

```python
def find_number(secret, low, high, max_steps=5):
    for step in range(1, max_steps + 1):
        guess = (low + high) // 2
        if guess == secret:
            return {"found": guess, "steps": step, "stopped": "done"}
        if guess < secret:
            low = guess + 1
        else:
            high = guess - 1
    return {"found": None, "steps": max_steps, "stopped": "max_steps"}

```

Let's trace the call `find_number(7, 1, 10)`: range 1 to 10, guess 5, too low, low = 6. Next guess is (6+10)//2 = 8, too high, high = 7. Next guess (6+7)//2 = 6, too low, low = 7. Next guess 7, found at step 4.

```python
print(find_number(7, 1, 10))                 # -> {'found': 7, 'steps': 4, 'stopped': 'done'}
print(find_number(7, 1, 10, max_steps=2))    # -> {'found': None, 'steps': 2, 'stopped': 'max_steps'}
```

`range(1, max_steps + 1)` counts the steps from 1. The result says **why** the loop stopped. For an agent the two reasons are `done` (the model answered) and `max_steps` (we cut it). You write this loop in the third exercise.

## Stop conditions

An agent should stop when:

| Reason | Meaning |
| --- | --- |
| **Done** | The model answered with no tool call |
| **Max steps** | Too many steps. A hard limit, always set |
| **Loop** | The same tool call again and again |
| **Budget** | Too many tokens, too much money or time (lesson 29) |
| **Error** | Something failed that the agent cannot fix |
| **Human** | A person must approve a risky step (lesson 30) |

Always return **why** it stopped, so your app can show a clear message and so you can count the failures.

### Catching a loop

A model that gets an unhelpful result may try the **exact same call** again. A cheap guard: count the calls by `name + arguments`. If one call is made more than 2 times, stop. This saves steps and money, and it is the fourth exercise.

## Tool errors are information

When a tool fails, do not crash. Send the error text back as the tool result: `error: city not found`. The model reads it and often fixes its own call (a different spelling, a different tool). That is what makes agents robust. But a repeating error is also how a loop starts, so the guard above matters.

## A trace helps you see what happened

Agents are hard to debug because the path is different each time. Keep the messages list (it is your trace) and print the tool calls and results while you build. In lesson 29 you will log them. Read a few traces by eye every time you change a prompt.

## Try it live

Make two tools with simple schemas (lesson 11): `get_price(item)` (a dictionary lookup) and `add(a, b)`.

1. Ask: *"What is the price of a pen plus the price of a book?"* The model has to call `get_price` twice, then `add`. Print the messages after each step.
2. Count the steps. Does the model call both prices in one step (parallel calls) or one by one?
3. Ask for a price of an item that does not exist. What does the tool return? Does the model recover or loop?
4. Set `max_steps=2` and watch the `max_steps` result.
5. Print the length of the messages list after each step. See how the history grows.

## A little deeper

- **Workflow vs agent.** If you already know the steps ("always search, then answer"), write the code yourself. That is a **workflow**: predictable, cheap, easy to test. Use an agent only when the steps depend on what the model finds. Many products need only a workflow.
- **Parallel calls** (lesson 11): when the model asks for several tools in one step, they are independent, so you may run them at the same time.
- **Thinking models** (lesson 34) can plan before each tool call. They are slower and cost more thinking tokens, but they often need fewer steps.
- **Context growth.** Long tool results fill the history fast. Cut results to a safe length, and summarize old steps when the history gets big (memory, lesson 12).
- **Tool descriptions are the control panel.** Most agent mistakes are tool mistakes: unclear names, unclear descriptions, too many tools, tools that return too much. Few, clear tools beat many vague ones.
- **Names to know.** The loop you wrote is the base of patterns such as **ReAct** (reason, then act, then observe), plan-and-execute, and reflection. Frameworks (LangChain, LangGraph) give you ready loops. The agentic track will cover them. You understand them now because you wrote the loop.
- **Reliability is a numbers game.** If each step is right 95% of the time, 10 steps are right only about 60% of the time (0.95 to the power 10). More steps mean more chances to fail.

## Common mistakes

- No `max_steps`, so a stuck agent runs (and bills) forever.
- Forgetting to put the model's tool request in the history.
- Changing the same list in place and losing the earlier history.
- Crashing when a tool fails, instead of returning the error text.
- Using an agent where a fixed workflow would do.
- Giving the agent many tools with vague descriptions.
- Never reading a trace.
- Ignoring that every step resends and pays for the whole history.

## Interview corner

**What is an agent, in one sentence?**
A loop where a model chooses actions (tool calls), your code runs them and returns the results, and the model decides when it is done.

**What is the difference between a workflow and an agent?**
In a workflow the code decides the steps. In an agent the model decides them at run time. Workflows are more predictable and cheaper. Agents handle open-ended tasks.

**How do you stop an agent from running forever?**
A hard `max_steps`, a loop check on repeated identical calls, a token or cost budget, and a time limit. Return the reason it stopped.

**Why does an agent cost more than a single call?**
Each step resends the whole history, and the history grows with every tool call and result, so the cost grows faster than the number of steps.

**What happens when a tool fails?**
Return the error text as the tool result, so the model can correct its call. Guard against the same failing call repeating.

## Summary

- An agent is a loop: model picks tool calls, code runs them, results go back, repeat until the model answers without a tool call.
- The history is the memory. You resend all of it every step, so cost grows with each step.
- A step = one model call plus running the requested tools. Keep the model's own message in the history.
- Always set `max_steps`, and return why the loop stopped (`done`, `max_steps`, `loop`).
- Catch loops by counting identical `name + arguments` calls.
- Tool errors go back as text, not as crashes.
- Prefer a plain workflow when the steps are known. Use an agent when they are not.
- Reference: `reference/genai-groq.md`.
