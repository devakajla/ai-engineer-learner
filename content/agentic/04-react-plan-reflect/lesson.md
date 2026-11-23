---
title: ReAct, plan-and-execute and reflection
summary: Learn three ways to make an agent think - ReAct (act step by step), plan-and-execute (plan first, then run) and reflection (check and improve) - and build each one in plain Python.
plan_ids: []
---

In lesson 1 you learned when to use an agent. In GenAI lesson 27 you built the agent loop. Now the question is: **how should the agent think?** Three ideas come up again and again, in papers, in frameworks and in interviews:

- **ReAct**: think a little, act, look at the result, repeat.
- **Plan-and-execute**: write the whole plan first, then run it step by step.
- **Reflection**: look at your own work, find what is wrong, and fix it.

They are not rivals. They are tools. Often you mix them.

## ReAct: Reason and Act

**ReAct** means *Reasoning + Acting*. The model alternates between a short thought and an action:

```
Thought: I need the price of the book.
Action: search_price
Action Input: {"title": "Dune"}
Observation: 12 dollars
Thought: Now I can answer.
Final Answer: The book costs 12 dollars.
```

- **Thought**: the model says what it plans to do next, in words. Writing the thought helps it choose the next action (like thinking step by step, GenAI lesson 7).
- **Action** and **Action Input**: the tool and its arguments.
- **Observation**: the tool result. Your code writes this line, **not** the model.
- **Final Answer**: the model is done.

Your code is a loop: call the model, parse the reply, run the tool, add the observation, call again. You wrote this loop with native tool calls in GenAI lesson 27, and you wrote `parse_react` in GenAI lesson 31. ReAct is the **same loop**, but with the action written as plain text.

### Why native tool calls replaced the text format

The original ReAct used text lines, and you had to parse them. That is fragile: one wrong line and the parse fails. Today the API offers **native tool calling** (GenAI lesson 11): the tool name and arguments come back as structured data. It is more reliable, so use it in real code.

But the **idea** of ReAct lives on in every agent: reason, act, observe, repeat. Many frameworks call their basic agent a "ReAct agent". And the text format is still handy to know, because it works with any model, even one with no tool support.

### Step by step: the loop with a text format (exercise 4)

Let's practise the shape of the last exercise with a different example. A little robot answers in text lines. A line `TOOL double 4` asks for a tool. A line `DONE ...` is the final answer. The replies come from a fixed list, so you can see the loop without a model. In your exercise the replies come from a model, and the parsing is done by `parse_react`.

1. Loop at most `max_steps` times, counting the step number from 1.
2. Take the next reply. If it starts with `DONE `, return the answer.
3. Otherwise split it, run the tool (or make an error text for an unknown tool), and remember the observation.
4. If the loop ends with no answer, return `None` and say that the limit was reached.

```python
def double(n):
    return n * 2

tools = {"double": double}

def run_robot(replies, tools, max_steps=5):
    history = []
    for step in range(1, max_steps + 1):
        reply = replies[step - 1]
        history.append("robot: " + reply)
        if reply.startswith("DONE "):
            return {"answer": reply[5:], "stopped": "done", "steps": step}
        _, name, arg = reply.split(" ")
        if name not in tools:
            observation = "error: unknown tool " + name
        else:
            observation = str(tools[name](int(arg)))
        history.append("result: " + observation)
    return {"answer": None, "stopped": "max_steps", "steps": max_steps}

print(run_robot(["TOOL double 4", "TOOL double 10", "DONE 20 is the last"], tools))
# -> {'answer': '20 is the last', 'stopped': 'done', 'steps': 3}
print(run_robot(["TOOL double 1"] * 3, tools, max_steps=2))
# -> {'answer': None, 'stopped': 'max_steps', 'steps': 2}
print(run_robot(["TOOL fly 1", "DONE ok"], tools))
# -> {'answer': 'ok', 'stopped': 'done', 'steps': 2}
```

`history` shows what a real agent keeps: every model reply and every observation, added in order. A real agent sends this history back to the model each step.

### ReAct: strengths and weaknesses

- **Good**: flexible. It handles tasks where the next step depends on the last result. Easy to build and to read.
- **Weak**: it decides **one step at a time**, with no overview. On long tasks it can wander, repeat itself, or forget the goal. Every step is a model call, so it can be slow and costly.

## Plan-and-execute

> First **plan** the whole task. Then **execute** the steps one by one.

Two phases:

1. **Planner** (one call): "Write a numbered plan for this goal."
2. **Executor** (one call per step): do step 1, then step 2, and so on. Each step sees the goal, the plan and the earlier results.
3. Optional **replan**: after a few steps, or when a step fails, ask the planner to update the plan with what you have learned.

Why use it:

- The model sees the **big picture** first, so it wanders less.
- The plan can be **shown to the user** (or a human) for approval *before* anything runs. That is a safety win.
- Executor steps can use a **cheaper model** than the planner.
- Independent steps can run **in parallel**.

The price: the plan can be wrong, because it is written before the facts are known. If step 2 shows that step 3 makes no sense, a fixed plan keeps going. That is why real systems replan.

You will build three small pieces: read the plan text, build the messages for each step, and run the steps with a hard limit.

### Step by step: read a plan (exercise 1)

The model writes the plan as text. Your code needs a **list**. Let's practise with a different example: a shopping list. Lines like `1. milk` and `2) eggs` are items. All other lines are ignored.

1. Go line by line and strip the spaces.
2. Count the digits at the start of the line.
3. If there are digits and then `.` or `)`, the rest is the item. Keep it unless it is empty.

```python
def parse_list(text):
    items = []
    for line in text.splitlines():
        line = line.strip()
        i = 0
        while i < len(line) and line[i].isdigit():
            i += 1
        if i == 0 or line[i:i + 1] not in (".", ")"):
            continue
        item = line[i + 1:].strip()
        if item:
            items.append(item)
    return items

print(parse_list("Shopping:\n1. milk\n2) eggs\n\nThanks!"))   # -> ['milk', 'eggs']
print(parse_list("no list"))                                  # -> []
```

`line[i].isdigit()` is `True` for `"7"` and `False` for `"a"`. `continue` skips to the next line. Why `line[i:i + 1]` and not `line[i]`? A slice never crashes at the end of the text. It just gives an empty text.

### Step by step: the message for one step (exercise 2)

A step call must carry everything the model needs: the goal, the whole plan, the results so far, and the current step. Let's practise with a different example: a note for a relay race runner.

1. Number the legs from 1 with `enumerate(..., start=1)`.
2. Take only the finished results, `times[:i]`. If there are none, write `(none yet)`.
3. Join the parts with blank lines.

```python
def relay_note(team, legs, times, i):
    numbered = "\n".join(f"{n}. {leg}" for n, leg in enumerate(legs, start=1))
    done = times[:i]
    if done:
        so_far = "\n".join(f"{n}. {t}" for n, t in enumerate(done, start=1))
    else:
        so_far = "(none yet)"
    return f"Team: {team}\n\nLegs:\n{numbered}\n\nTimes so far:\n{so_far}\n\nNow running (leg {i + 1} of {len(legs)}): {legs[i]}"

print(relay_note("Reds", ["Anna 100m", "Raj 200m"], ["12s"], 1))
# -> Team: Reds
# ->
# -> Legs:
# -> 1. Anna 100m
# -> 2. Raj 200m
# ->
# -> Times so far:
# -> 1. 12s
# ->
# -> Now running (leg 2 of 2): Raj 200m
```

`i` starts at 0, so the first step shows `i + 1`.

### Step by step: run the plan with a limit (exercise 3)

Let's practise with a different example: run chores, but never more than `limit` of them, and report what was skipped. Here "doing a chore" is a plain function that sees what was done before.

1. Take the part to run: `chores[:limit]`.
2. Run each one and keep the result.
3. Report how many ran and how many were skipped.

```python
def do_chore(chore, done_so_far):
    return f"{chore} (after {len(done_so_far)} done)"

def run_chores(chores, limit):
    results = []
    to_run = chores[:limit]
    for i in range(len(to_run)):
        results.append(do_chore(to_run[i], results))
    return {"results": results, "steps_run": len(to_run), "skipped": len(chores) - len(to_run)}

print(run_chores(["wash", "sweep", "paint"], 2))
# -> {'results': ['wash (after 0 done)', 'sweep (after 1 done)'], 'steps_run': 2, 'skipped': 1}
print(run_chores([], 5))
# -> {'results': [], 'steps_run': 0, 'skipped': 0}
```

A slice like `chores[:2]` on a list with 1 item is fine: it just gives that item. In your exercise "doing a step" is a model call with the messages from exercise 2.

## Reflection

> Look at your own output, say what is wrong, and fix it.

You already built this in lesson 3 as the **evaluator-optimizer** loop: draft, judge, revise, stop at a limit. In agent talk it is called **reflection** or **self-critique**. It can run inside an agent too: after the agent writes an answer, a critique step checks the answer against the question and the sources, and the agent revises.

When it works well:

- There is **outside feedback**: tests that fail, a schema check, a search that finds no source for a claim. The model then fixes a real problem.
- The criteria are **clear**: "every claim needs a citation", "the code must pass these tests".

When it works badly:

- The model only judges itself, with no outside signal. It may praise its own mistake, or "fix" something that was right.
- There is no limit, so it loops.

Rule of thumb: **prefer a checker made of code** (tests, validation, rules) over a model that says "looks good". Use a model judge only for what code cannot check, like tone or helpfulness.

## Comparing the three

| | ReAct | Plan-and-execute | Reflection |
| --- | --- | --- | --- |
| **Idea** | Think, act, observe, repeat | Plan first, then run the steps | Critique and revise |
| **Who decides the next step** | The model, one step at a time | The plan (fixed, or replanned) | The critique |
| **Best for** | Open tasks, unknown steps | Long tasks with clear parts | Quality against clear criteria |
| **Risk** | Wanders, repeats | A wrong plan stays wrong | Loops, self-praise |
| **Cost** | One call per step | One plan call plus one per step | Extra calls per round |
| **Needs** | Tools and a loop limit | A plan parser and a step limit | A judge, and a round limit |

They mix well. A common design: **plan**, then a small **ReAct** loop for each step, then a **reflection** check on the final answer, all under a **step budget**.

## Try it live

Use your `run_agent` from GenAI lesson 27 and the question *"What is the total price of 3 books at the price of Dune, and is it more than 40?"* with two fake tools, `search_price(title)` and `multiply(a, b)`.

1. Run it as a **ReAct** agent (native tool calls). Print every step. How many model calls?
2. Run it as **plan-and-execute**: one call for the plan (parse it with `parse_plan`), then `execute_plan`. Compare the calls and the tokens.
3. Add a **reflection** step: ask the model to check the final answer against the tool results. Does it ever change a right answer to a wrong one?
4. Break a tool on purpose (make it raise an error). Which approach recovers best?

## A little deeper

- **Native tool calls vs text.** With native tool calls, the "Thought" is often hidden or short. Reasoning models (GenAI lesson 34) think inside before they act, so a visible `Thought:` line adds little.
- **Replanning.** After each step you can ask: "Is the plan still good given this result?" Replan only when the answer is no, or you pay a call per step for nothing.
- **Plan as data.** Ask the planner for JSON (`[{"step": ..., "tool": ...}]`) and validate it with Pydantic (GenAI lesson 10). Then you can check each tool name *before* running anything.
- **Parallel steps.** If steps do not depend on each other, run them together. A plan that marks dependencies is called a **DAG** (a graph with no loops). LangGraph (week 7) is built for this.
- **Reflexion.** A known idea: after a failed try, the agent writes a short lesson ("I forgot to check the date") into its memory, and uses it on the next try.
- **Self-consistency again.** For a hard step, run it 3 times and vote (GenAI lesson 7). It is reflection's cheaper cousin.
- **Budget.** Every approach needs limits: max steps, max tokens, max seconds. You meet them again in the next lesson.

## Common mistakes

- Parsing a model's plan with `split("\n")` and trusting every line.
- Running a plan with no step limit.
- Showing the executor only the current step, with no goal and no earlier results.
- Never replanning when a step fails.
- Reflection with no outside check, so the model just agrees with itself.
- No round limit on a reflection loop.
- Using a heavy plan-and-execute design for a task that one tool call can solve.
- Sending the Observation back without the model's own reply, so it forgets what it asked.

## Interview corner

**What is ReAct?**
A pattern where the model alternates **reasoning** (a short thought) and **acting** (a tool call), reads the observation, and repeats until it can give a final answer. It is the base loop of most agents.

**What is the difference between ReAct and plan-and-execute?**
ReAct chooses one step at a time with no overview. Plan-and-execute writes the full plan first, then runs it. A plan gives a big picture, can be reviewed before it runs and can use cheaper models for steps, but it can be wrong and needs replanning.

**When does reflection help and when does it not?**
It helps with outside feedback (tests, validators, missing sources) and clear criteria. It helps little when the model only judges itself, and it can loop, so it needs a round limit.

**How would you stop an agent from running for ever?**
Limit steps, tokens, time and cost. Detect loops (same tool and arguments again and again). Return a clear message when a limit is reached, with the partial result.

**Why did native tool calling replace the text ReAct format?**
Structured tool calls are more reliable than parsing text. The ReAct idea stays, only the format changed.

## Summary

- **ReAct**: thought, action, observation, repeat, until a final answer. Text format: `Thought:`, `Action:`, `Action Input:`, `Observation:`, `Final Answer:`. Today native tool calls do the same job.
- **Plan-and-execute**: plan first (`parse_plan` turns the text into a list), then run each step with the goal, the plan and the earlier results (`build_step_messages`), under a step limit. Replan when needed.
- **Reflection**: critique and revise (the evaluator-optimizer loop). Best with outside feedback and a hard round limit.
- Mix them: plan, ReAct inside each step, reflect on the result, and cap everything with a budget.
- Reference: `reference/genai-groq.md`.
