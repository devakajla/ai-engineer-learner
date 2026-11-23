---
title: Workflow or agent? When NOT to use an agent
summary: Learn the difference between a workflow and an agent, why errors pile up over many steps, and how to choose the simplest approach that works.
plan_ids: []
---

In the GenAI track you learned to call a model, use tools, and build RAG. Now you will build **agents**. Before you write one, you need to learn the most useful skill of an agent engineer:

> Knowing when **not** to build an agent.

Agents are exciting. They are also slower, costlier, harder to test, and less predictable than plain code. Many tasks that look like "agent problems" are better solved with one model call, or with a few model calls in a fixed order. A good engineer picks the **simplest** thing that works. In interviews this question comes up very often: "Would you use an agent here?"

## Three words

- **Workflow**: your **code** decides the steps. The model may be called in some of the steps, but the path is fixed. Example: step 1 extract the invoice fields, step 2 check them, step 3 save them. Always in this order.
- **Agent**: the **model** decides the steps. You give it a goal and some tools. It chooses which tool to call next, and when to stop. You will build the loop in GenAI lesson 27.
- **Tool**: a function the model may ask your code to run (GenAI lesson 11).

A simple way to remember it:

```
workflow:  your code holds the steering wheel
agent:     the model holds the steering wheel
```

## A ladder of options

Think of a ladder. Start at the bottom. Climb only if the step below is not enough.

```
1. one model call                      <- cheapest, fastest, easiest to test
2. a few calls in a fixed order        <- "prompt chain" (the next lessons)
3. a workflow with tools and branches  <- code decides, model fills the gaps
4. an agent with tools                 <- model decides the steps
5. several agents working together     <- hardest to build and debug (week 8)
```

Most production systems live on steps 1 to 3. Step 4 is used for the open-ended tasks that really need it.

## Why not use an agent for everything?

An agent loop has a price. Look at it honestly:

| What | Workflow | Agent |
| --- | --- | --- |
| **Steps** | Fixed, you know them | Chosen at run time, different each time |
| **Cost** | Predictable | Grows with every step (the whole history is sent again) |
| **Speed** | Fast | Slow: each step is a model call |
| **Testing** | Easy: same input, same path | Hard: many possible paths |
| **Debugging** | Read the code | Read a long trace |
| **Safety** | You control each action | The model may choose a bad action |
| **Good at** | Known, repeatable tasks | Open-ended tasks with unknown steps |

The biggest hidden cost is **errors that pile up**.

### Errors multiply

Suppose each step of a run works 95% of the time. That sounds great. But if the run needs 10 steps in a row, **all** of them must work. The chances are multiplied:

```python
0.95 * 0.95 * 0.95   # -> about 0.857  (3 steps)
0.95 ** 10           # -> 0.5987... (10 steps: the run works only about 6 times in 10)
```

`**` is the power operator. `0.95 ** 10` means 0.95 multiplied by itself 10 times.

So a longer run is much less reliable than one step, even when every step is good. A workflow has few, fixed steps. An agent may take 10 or 20. That is a big reason to keep agents short, and to prefer a workflow when the steps are known.

### Step by step: the chance that a whole run works

Let's practise the shape of the first exercise with a different example. A cook makes a dish in a number of steps. Each step works with a chance. What is the chance that all the steps work? If there are no steps, nothing can fail.

1. If the number of steps is 0 or less, return `1.0`.
2. Otherwise multiply the chance by itself `steps` times with `**`.
3. Round the result so it is easy to read.

```python
def dish_works(step_chance, steps):
    if steps <= 0:
        return 1.0
    return round(step_chance ** steps, 3)

print(dish_works(0.9, 4))    # -> 0.656
print(dish_works(0.9, 0))    # -> 1.0
```

In your first exercise you do the same, and also refuse a chance that is not between 0 and 1.

## When an agent IS the right choice

Use an agent when **all** of these are true:

1. The task needs **tools** (search, a database, an API). Otherwise one call is enough.
2. You **cannot know the steps in advance**. Which tool is needed next depends on what the last tool returned.
3. A **wrong step is cheap** to undo or to catch (a search query, a draft). Or a human approves the risky steps.
4. The task is **worth the cost**: the answer is valuable enough to pay for 5 to 20 model calls.

Good examples:

- Research a question across several web pages and write a short report.
- Find and fix a bug in a code base: read files, run tests, try a fix.
- Answer a support question that may need an order lookup, a policy lookup, or both.

## When NOT to use an agent

- **You know the steps.** "Extract fields, validate, save" is a workflow. Write it as code.
- **One call is enough.** Classify a text, summarize a page, translate. No tools, no loop.
- **Speed matters.** A user waiting for an answer in a chat box will not wait 30 seconds.
- **The action is risky and cannot be undone.** Payments, deletes, emails to customers. Use a fixed workflow with a human approval step.
- **You need exactly the same result each time.** Agents vary.
- **The cost per request must be tiny.** An agent can cost 10 to 50 times more than a single call.

A short checklist you can say in an interview:

1. Does it need tools? If not, **one call**.
2. Do I know the steps? If yes, **workflow**.
3. Can the steps vary a lot with the input? Then consider an **agent**.
4. Is the action risky? Add **human approval** and limits.
5. Is it worth the cost and the delay? If not, **simplify**.

### Step by step: a decision function

Let's practise the shape of the second exercise with a different example: choose how to move a parcel. A short trip needs no vehicle (walk). A known route needs a bus. An unknown route needs a taxi, and an expensive parcel needs a taxi with a guard. The rules are checked in order, and the first rule that fits decides.

1. No vehicle needed? Return `"walk"`.
2. Route known? Return `"bus"`.
3. Expensive? Return `"taxi_with_guard"`.
4. Otherwise `"taxi"`.

```python
def move_parcel(needs_vehicle, route_known, expensive=False):
    if not needs_vehicle:
        return "walk"
    if route_known:
        return "bus"
    if expensive:
        return "taxi_with_guard"
    return "taxi"

print(move_parcel(False, True))        # -> walk
print(move_parcel(True, False, True))  # -> taxi_with_guard
```

## Measure, then choose

Opinions about "what is better" are weak. Numbers are strong. Build a small test set (10 to 30 real questions, GenAI lesson 37), run each approach on it, and write down three numbers:

- **success**: the share of questions answered correctly,
- **cost** per question,
- **time** per question.

Then decide with a rule such as: "the cheapest approach with at least 90% success and under 10 seconds".

### Step by step: pick from the numbers

Let's practise the shape of the third exercise with a different example: choose a bike from a list. A bike is good enough if its speed is high enough and its price is low enough. Among the good ones, take the cheapest.

1. Build a list `good` of the bikes that pass both limits.
2. If it is empty, return `None`.
3. Otherwise find the one with the lowest price. A small helper function tells `min` what to compare.

```python
def by_price(bike):
    return bike["price"]

def pick_bike(bikes, min_speed, max_price):
    good = []
    for bike in bikes:
        if bike["speed"] >= min_speed and bike["price"] <= max_price:
            good.append(bike)
    if not good:
        return None
    return min(good, key=by_price)["name"]

bikes = [
    {"name": "city", "speed": 20, "price": 300},
    {"name": "road", "speed": 35, "price": 900},
    {"name": "race", "speed": 45, "price": 2000},
]
print(pick_bike(bikes, 30, 1000))   # -> road
print(pick_bike(bikes, 50, 1000))   # -> None
```

`min(items, key=function)` returns the item for which the function gives the smallest value. To break ties, make the function return a **tuple** like `(price, name)`. Python compares tuples from the left, so the name only matters when the prices are equal. Your exercise needs `(cost, seconds, name)`.

## Start simple, and escalate

A very common production pattern:

1. Try the **cheap** path first (one call, or a lookup in a table).
2. Check the result with a **simple rule** (is it empty? does it say "I am not sure"? does it fail validation?).
3. Only if the check fails, run the **expensive** path (the agent).

This is called **escalation**. Most requests are easy, so most requests stay cheap. Only the hard ones pay for the agent.

### Step by step: escalate

Let's practise the shape of the fourth exercise with a different example: a help desk. First look in a small dictionary of answers. If the question is not there, ask an expert (the slow path).

1. Try the cheap function.
2. If its answer is good enough, return it and say `"cheap"`. The expert is **not** called.
3. If it fails or raises an error, call the expert.

```python
def ask_help_desk(question, lookup_fn, expert_fn, is_good):
    try:
        answer = lookup_fn(question)
    except Exception:
        return {"answer": expert_fn(question), "used": "expert"}
    if is_good(answer):
        return {"answer": answer, "used": "cheap"}
    return {"answer": expert_fn(question), "used": "expert"}

FAQ = {"opening hours": "9 to 5"}

def lookup(q):
    return FAQ[q]            # a KeyError when the question is not in the FAQ

def expert(q):
    return "Let me check that for you."

def is_good(answer):
    return len(answer) > 0

print(ask_help_desk("opening hours", lookup, expert, is_good))
# -> {'answer': '9 to 5', 'used': 'cheap'}
print(ask_help_desk("refund rules", lookup, expert, is_good))
# -> {'answer': 'Let me check that for you.', 'used': 'expert'}
```

Notice that all three helpers are **passed in as arguments**. That keeps `ask_help_desk` simple and easy to test with fakes, which is exactly what your fourth exercise does.

## Try it live

Pick one task: *"Is this customer email about billing, shipping, or something else? Then write a two-line reply."*

1. Solve it with **one** call. Time it, and note the tokens (`response.usage`).
2. Solve it with **two** calls in a fixed order: classify, then reply with a prompt for that class.
3. Solve it as an **agent** (use your `run_agent` from GenAI lesson 27 once you have it, with a fake `lookup_policy` tool).
4. Write a small table: success on 5 emails, time, tokens, for each approach. Which one would you ship? Write one sentence why.

## A little deeper

- **A spectrum, not two boxes.** Real systems mix both: a workflow whose one step is a small agent loop with a limit. Use as little "agent" as you need.
- **"Agentic" is a matter of degree.** The more control you give the model over the steps, the more agentic the system is, and the more checks you need.
- **Latency budget.** Chat UIs feel good under 2 to 3 seconds for the first token. Background jobs (reports, research) can take minutes, so agents fit there better.
- **Cost of failure.** If a wrong answer costs a lot (money, health, trust), prefer fixed workflows plus human review.
- **Models improve.** A task that needed an agent last year may be solved by one call today. Re-test your choice now and then.
- **Frameworks tempt you.** A framework makes it easy to add agent loops. Easy is not the same as needed. Start with plain Python (this level), then use a framework only when it saves you real work.

## Common mistakes

- Starting with a multi-agent design for a task that one call can do.
- Calling a fixed sequence of model calls an "agent". If the code decides the order, it is a workflow. (That is fine. It is often the better choice.)
- Forgetting that errors multiply with the number of steps.
- Choosing by feeling, with no test set and no numbers.
- Giving an agent risky tools with no approval step and no limits.
- No fallback: when the agent fails, the user sees nothing. Escalate to a human or return a clear message.

## Interview corner

**What is the difference between a workflow and an agent?**
In a workflow, code decides the path and the model is called inside fixed steps. In an agent, the model decides the next step in a loop, by choosing tool calls, until it decides it is done.

**When would you not use an agent?**
When one call is enough, when the steps are known, when latency or cost must be low, when actions are risky and irreversible, or when you need repeatable results. Use a workflow, or one call, instead.

**Why can long agent runs be unreliable even if each step is good?**
The chances multiply. At 95% per step, 10 steps succeed together only about 60% of the time. Keep runs short, validate between steps, and add limits and retries.

**How do you decide between approaches?**
Build a small test set, run each approach, and compare success, cost and latency. Pick the simplest approach that meets the targets. Re-check when models change.

**What is escalation?**
Try the cheap path first, check its result with a simple rule, and run the expensive path (the agent) only when the check fails.

## Summary

- **Workflow**: code decides the steps. **Agent**: the model decides, in a loop, with tools.
- Climb the ladder one step at a time: one call, a fixed chain, a workflow with tools, an agent, several agents.
- Agents cost more, are slower, harder to test and less predictable. Errors multiply: `0.95 ** 10` is about 0.6.
- Use an agent only when tools are needed, the steps are unknown, a wrong step is cheap or approved, and the task is worth the cost.
- Checklist: tools? known steps? varying steps? risky? worth it?
- Choose with numbers: success, cost and time on a test set.
- Start simple and escalate to the agent only when a cheap check fails.
- Reference: `reference/genai-groq.md`.
