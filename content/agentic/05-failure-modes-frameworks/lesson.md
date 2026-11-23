---
title: Why agents fail, and a map of frameworks
summary: Learn the common ways agents fail (loops, bad tools, runaway cost, drift), how to stop them with budgets and checks, how to test the path an agent took, and how the main agent frameworks compare.
plan_ids: []
---

This is the Saturday lesson of week 6: lighter, and about the **big picture**. You can build an agent now. This lesson is about two things that decide whether it survives in real life:

1. **How agents fail**, and how to catch it.
2. **Which framework to use**, or whether to use one at all.

## How agents fail

Agents fail in a small number of ways. Learn the list, and you can debug most problems fast.

| Failure | What you see | Usual cause | Fix |
| --- | --- | --- | --- |
| **Loop** | Same tool, same arguments, again and again | The tool result does not help, and the model tries the same thing | Detect repeats, tell the model "you already tried this", stop after N |
| **Error streak** | Many tool errors in a row | Bad arguments, a broken tool, or a vague tool description | Better error texts, argument validation, stop and ask for help |
| **Wrong tool** | The model picks an unfit tool | Overlapping or vague descriptions, too many tools | Fix descriptions, fewer tools (lesson 2) |
| **Bad arguments** | Wrong types, made-up ids | The model guessed | Validate, return an error that says what is expected |
| **Runaway cost** | A single request costs far too much | Many steps, huge tool results, a big history | Budgets, truncate results, cache, cheaper model for easy steps |
| **Too slow** | The user waits a minute | Many sequential calls | Fewer steps, parallel calls, stream progress |
| **Drift** | The agent forgets the goal in a long run | A long history, the goal gets lost in the middle | Repeat the goal, summarize the history, plan first |
| **Hallucinated success** | "Done!" when nothing was done | The model claims, no check | Verify with code (did the file change? did the test pass?) |
| **Prompt injection** | A web page tells the agent to do something bad | Tool results are treated as instructions | Treat tool output as data, limit tool power, approvals (GenAI lessons 30 and 37) |
| **Unsafe action** | A delete or a payment happens by mistake | Powerful tools with no approval | Read-only by default, human approval, small permissions |

Almost every fix on the right is **code**, not a better prompt. A careful agent is mostly good plumbing around the model.

### Step by step: spot a loop and a streak (exercise 1)

Let's practise the shape of the first exercise with a different example: a vending machine log. Each press is a dictionary `{"button": ..., "result": ...}`. We want to find: a button pressed 3 or more times (`repeat`), 2 or more `jam` results in a row (`jam_streak`), and too many presses (`too_many`).

1. For each press, count how many presses in the log used the same button.
2. For the streak, keep a counter that grows on a jam and goes back to 0 otherwise. Remember the biggest value.
3. Add a label for each problem found, in a fixed order.

```python
def check_log(log, max_presses=6):
    found = []
    repeated = False
    for press in log:
        same = 0
        for other in log:
            if other["button"] == press["button"]:
                same += 1
        if same >= 3:
            repeated = True
    if repeated:
        found.append("repeat")
    streak = 0
    worst = 0
    for press in log:
        if press["result"].startswith("jam"):
            streak += 1
            worst = max(worst, streak)
        else:
            streak = 0
    if worst >= 2:
        found.append("jam_streak")
    if len(log) >= max_presses:
        found.append("too_many")
    return found

log = [{"button": "A1", "result": "jam"}, {"button": "A1", "result": "jam"}, {"button": "A1", "result": "chips"}]
print(check_log(log))                                      # -> ['repeat', 'jam_streak']
print(check_log([{"button": "B2", "result": "tea"}]))      # -> []
```

The loop inside a loop counts, for each press, how many presses match it. It is slow for a huge log, but a trace has only a few dozen steps, so it is fine.

## Budgets: hard limits for every run

A **budget** is a set of limits you check **before every step**:

- **max steps**: stops loops.
- **max tokens**: stops a growing history.
- **max cost** (money): stops a surprise bill.
- **max seconds**: stops a hung run.

When a limit is reached, stop **cleanly**: return a clear message and the partial result (not a crash and not silence). The `max_steps` guard in your GenAI lesson 27 loop is the first limit. Add the others as you go.

> Budgets are a **safety net, not a design**. If an agent often hits its limit, fix the tools or the prompt instead of raising the limit.

### Step by step: check a budget (exercise 2)

Let's practise the shape of the second exercise with a different example: a phone plan. It has a limit of calls and a limit of data. Return the name of the first limit that is used up, or `None`. A missing limit is not checked.

1. List the pairs `(limit name, used name)` in the order to check.
2. For each pair, if the limit exists and the used amount is at least the limit, return its name.
3. If nothing is used up, return `None`.

```python
def check_plan(used, limits):
    names = [("max_calls", "calls"), ("max_data", "data")]
    for limit_name, used_name in names:
        if limit_name in limits and used.get(used_name, 0) >= limits[limit_name]:
            return limit_name
    return None

print(check_plan({"calls": 10, "data": 2}, {"max_calls": 60, "max_data": 5}))   # -> None
print(check_plan({"calls": 60}, {"max_calls": 60}))                             # -> max_calls
print(check_plan({}, {}))                                                       # -> None
```

`used.get("data", 0)` returns 0 when the key is missing, so a plan with no data used yet does not crash.

## Seeing what happened: traces

You cannot fix what you cannot see. Keep a **trace** of every run: each model call, each tool call with its arguments and result, the tokens, the time and the cost. A trace is just a list of dictionaries, saved to a file or a service.

With traces you can:

- **Debug**: read the steps of a failed run in order.
- **Detect failures** automatically (loops, error streaks), as in exercise 1.
- **Test the path**: compare the tools the agent called with the tools it should have called.
- **Measure**: average steps, cost and time per request.

In week 9 you meet tracing tools (Langfuse, LangSmith). They store traces for you and show them in a web page. The idea is the same as your list of dictionaries.

### Testing the path (trajectory evaluation)

For many tasks you know **which tools** the agent should use and in what order. Compare it with what it did:

- Were all the needed tools called?
- In the right order (other calls may sit between)?
- Were there extra calls (wasted cost)?

It is cheap, needs no model judge, and catches a lot. It does not check if the final **answer** is good, so use it together with an answer check (GenAI lesson 41).

### Step by step: is the order right? (exercise 3)

Let's practise the shape of the third exercise with a different example: a recipe. Did the cook do the recipe steps **in order**, even with other things between them? Move a pointer through the recipe each time the cook's step matches the next recipe step.

1. Start the pointer at 0.
2. For each cooked step: if it equals `recipe[pointer]`, move the pointer on.
3. If the pointer reached the end of the recipe, the order was right.

```python
def steps_in_order(recipe, cooked):
    position = 0
    for step in cooked:
        if position < len(recipe) and step == recipe[position]:
            position += 1
    return position == len(recipe)

print(steps_in_order(["chop", "fry"], ["wash", "chop", "salt", "fry"]))   # -> True
print(steps_in_order(["chop", "fry"], ["fry", "chop"]))                   # -> False
print(steps_in_order([], ["fry"]))                                        # -> True
```

An empty recipe is always "in order", because there is nothing to miss.

## A map of agent frameworks

A **framework** is a library with ready-made parts: an agent loop, tool wrappers, memory, tracing, and ways to connect many agents. The field changes very fast. **Check each project's docs before you rely on any detail here.** The ideas below are the stable part.

| Option | Main idea | Good for | Watch out for |
| --- | --- | --- | --- |
| **No framework** (plain Python) | You write the loop and the tools | Learning, small agents, full control | You build memory, tracing and retries yourself |
| **LangChain** | Large toolbox of model, prompt, tool and retriever parts | Fast prototypes, many integrations | Many layers, can be hard to debug |
| **LangGraph** | Agents as a **graph** of nodes and edges with shared state, saved checkpoints and human-in-the-loop | Long, stateful, controllable agents | More concepts to learn (week 7) |
| **CrewAI** | A **crew** of role-playing agents with tasks | Quick multi-agent demos | Less control over each step |
| **AutoGen** | Agents that **talk to each other** in conversations | Research on multi-agent chat | The project has changed a lot, check its state |
| **OpenAI Agents SDK** | Small set of ideas: agents, tools, **handoffs**, guardrails, tracing | Simple agents on OpenAI models (it can use other providers too) | Check what it supports for your provider |
| **Claude Agent SDK** | The agent loop and tools that Claude Code uses, as a library | Coding and file agents | Tied to Claude models |

How to choose, in short:

1. **Start with plain Python**, as in this level. You learn what a framework hides.
2. Add a framework when it **saves real work**: durable state, human approval, tracing, or many steps with branches. For that, **LangGraph** is a strong default in interviews and in production.
3. Do not choose by hype or by a demo. Choose by: how much control you need, how well you can debug it, how well it is maintained, and what your team knows.
4. Keep your **tools** and **prompts** independent of the framework, so you can switch.

> Frameworks are not required for a good agent. A good engineer can write the loop alone **and** knows when a framework is worth its weight.

## Try it live

Take your agent from GenAI lesson 27 and break it on purpose.

1. Give it a tool that always returns `error: try later`. Does it loop? Count the steps. Which of the three failure labels from exercise 1 would fire?
2. Add a `check_budget` call at the top of each step, with `max_steps=6` and `max_tokens=4000`. Print the label when it stops.
3. Save the trace of each run (a list of dictionaries) and run `detect_failure` and `check_tool_path` on it.
4. Read the docs of LangGraph and of one other framework. Write 3 lines: what does it add over your loop? What would you give up?

## A little deeper

- **Make failure visible to the user.** "I could not finish because I reached my step limit. Here is what I found so far: ..." is far better than silence.
- **Graceful degradation.** When the agent fails, fall back to a simpler path (a plain search, a canned answer, a human).
- **Loop hints.** When you detect a repeat, add a message to the history: "You already called this with the same arguments. Try something different or answer." It often breaks the loop.
- **Idempotent retries.** A step may be retried after a crash. Write tools so that a repeat is safe (lesson 2).
- **Cost is a metric.** Track average cost per request and the 95th percentile (GenAI lesson 29). One expensive tail run can hide behind a good average.
- **Evaluation of agents** (week 9) measures task success, steps, cost and time on a test set. This lesson's checks are the building blocks.
- **Frameworks and lock-in.** Prompts and tool schemas are portable. State formats and graph definitions usually are not.

## Common mistakes

- No limit on steps, tokens, cost or time.
- Raising the limit instead of fixing the cause.
- Stopping with no message, so the user sees nothing.
- Believing "Done!" without checking the result with code.
- Choosing a framework before building the plain loop once.
- Putting prompts and tool logic deep inside framework classes, so they cannot be moved.
- No traces, so failures cannot be reproduced.

## Interview corner

**What are the common failure modes of agents?**
Loops, error streaks, wrong tool or bad arguments, runaway cost and latency, drift in long runs, hallucinated success, prompt injection through tool results, and unsafe actions.

**How do you keep an agent from running up a huge bill?**
Set budgets for steps, tokens, cost and time and check them before every step. Truncate tool results, cache repeated work, use cheaper models for easy steps, and stop cleanly with a partial result.

**How do you test an agent?**
Use a fixed test set. Check the final answer (code checks and a judge), and check the path: which tools were called, in what order, and how many extra calls. Track steps, cost and time.

**How would you choose between LangGraph, CrewAI and no framework?**
Start with plain Python to learn the loop. Use LangGraph when you need durable state, branches, human approval and tracing. CrewAI suits quick multi-agent demos. Pick by control, debuggability, maintenance and team skill, not by hype.

**What would you do when an agent loops?**
Detect repeated tool calls with the same arguments, add a hint to the history, and stop after a limit with a clear message. Then find the root cause in the trace, usually a tool that gives no useful result.

## Summary

- Common failures: loop, error streak, wrong tool, bad arguments, runaway cost, slowness, drift, hallucinated success, prompt injection, unsafe actions. Most fixes are code.
- `detect_failure` reads a trace and labels `loop`, `error_streak` and `max_steps`.
- A **budget** (steps, tokens, cost, seconds) is checked before every step. `check_budget` returns the first limit reached. Stop cleanly with a message.
- Keep **traces**. Test the path with `check_tool_path`: all called, in order, extra calls.
- Frameworks: plain Python, LangChain, LangGraph, CrewAI, AutoGen, OpenAI Agents SDK, Claude Agent SDK. They change fast, so check the docs. Start plain, add a framework when it saves real work, and keep tools and prompts portable.
- Reference: `reference/genai-groq.md`.
