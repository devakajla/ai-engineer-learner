---
title: "Workflow patterns: chain, route, orchestrate, improve"
summary: Learn the five building blocks of LLM workflows - chain, route, parallel, orchestrator-workers and evaluator-optimizer - and when each one is the right tool.
plan_ids: []
---

In lesson 1 you learned that most real systems are **workflows**: your code decides the path, and the model does the thinking inside the steps. Workflows are cheaper, faster and easier to test than agents. So it pays to know the standard shapes.

There are five. Almost every LLM app you will meet is one of them, or a mix. Knowing their names also helps you in interviews: "Which pattern would you use here?"

Quick map:

```
1. Chain               A -> B -> C                   steps in a fixed order
2. Route               input -> pick -> handler      one path out of several
3. Parallel            A, B, C at the same time      split work, or vote
4. Orchestrator-worker plan -> workers -> combine    the model decides the subtasks
5. Evaluator-optimizer write -> judge -> rewrite     loop until good, with a limit
```

All five use only what you already know: functions, lists, loops and model calls. No framework is needed.

## A helper: `ask`

All the examples and exercises use one small function that makes one model call and returns the cleaned text:

```python
def ask(client, prompt, system=None, temperature=0):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b", messages=messages, temperature=temperature
    )
    return response.choices[0].message.content.strip()
```

One helper means one place to add timeouts, retries (GenAI lesson 6) and logging later.

## 1. Prompt chaining

> Split a task into steps. Each step is one model call. The output of one step is the input of the next.

Example: "write a blog post" becomes (1) write an outline, (2) write each section from the outline, (3) polish the tone. Each call has a **small, clear job**, so each is more reliable than one giant prompt.

You can add a **gate** between steps: a small check in plain code. If the outline has fewer than 3 points, stop or retry before you spend money on the next step.

Use a chain when the task splits into **fixed, ordered** parts.

### Step by step: a chain (exercise 1)

Let's practise the shape of the first exercise with a different example. Instead of model calls, each step here is a plain function that changes a text. The loop is the same: the output of one step is the input of the next, and you keep every output.

1. Keep a variable `current`, starting with the input.
2. For each step: call it with `current`, and save the result as the new `current`.
3. Return the last result and the list of all results.

```python
def clean(text):
    return text.strip()

def shout(text):
    return text.upper()

def add_bang(text):
    return text + "!"

def run_steps(steps, text):
    outputs = []
    current = text
    for step in steps:
        current = step(current)
        outputs.append(current)
    return {"result": current, "outputs": outputs}

print(run_steps([clean, shout, add_bang], "  hello "))
# -> {'result': 'HELLO!', 'outputs': ['hello', 'HELLO', 'HELLO!']}
print(run_steps([], "hi"))
# -> {'result': 'hi', 'outputs': []}
```

In your exercise each step is a prompt template with `{input}`, and "calling the step" means calling `ask`.

## 2. Routing

> Look at the input, pick a category, and send it to a handler made for that category.

Example: a support bot. Billing questions go to a handler with billing rules. Technical questions go to a handler with troubleshooting steps. Everything else goes to a general handler. Each handler has a short, focused prompt, and you can even use a **cheaper model** for easy categories.

The classifier is a small call at temperature 0. And you **never trust its format**: clean the reply, and use a safe default (`"other"`) when it is not a known label (GenAI lesson 7).

Use routing when the inputs are **clearly different kinds** that need different handling.

### Step by step: a router (exercise 2)

Let's practise the shape of the second exercise with a different example: a school office. A guess says which desk should handle a note. The guess is cleaned, and an unknown guess goes to the `"other"` desk.

1. Clean the guess: lowercase, remove a final dot.
2. If it is not a known desk, use `"other"`.
3. Call the handler of that desk.

```python
def handle_fees(note):
    return "Fees desk: " + note

def handle_exams(note):
    return "Exams desk: " + note

def handle_other(note):
    return "Front desk: " + note

DESKS = {"fees": handle_fees, "exams": handle_exams, "other": handle_other}

def send_note(guess, note):
    label = guess.lower().strip(".")
    if label not in DESKS:
        label = "other"
    return {"label": label, "answer": DESKS[label](note)}

print(send_note("Exams.", "When is the maths test?"))
# -> {'label': 'exams', 'answer': 'Exams desk: When is the maths test?'}
print(send_note("I think sports", "Is there a match?"))
# -> {'label': 'other', 'answer': 'Front desk: Is there a match?'}
```

Here the guess comes in as an argument. In your exercise it comes from a classifier call, and the handler is a second model call with a different **system prompt** for each label.

## 3. Parallelization

> Run several model calls **at the same time** and combine the results.

Two flavours:

- **Sectioning**: split the work into independent parts and run them together. Example: check one document for three things (spelling, tone, facts) with three calls at once, then merge the three reports.
- **Voting**: run the **same** task several times and take the majority (this is self-consistency from GenAI lesson 7). Example: ask 5 times if a code change is safe, and flag it if 2 or more say no.

The calls must not depend on each other. Running them together saves **time**, not money: the cost is the same or higher. Real code uses threads or `async` to run them at once (you meet async in Python lessons 30 and 31). In this level we keep calls one after the other, because the idea is the same.

Use parallelization when parts are independent and **speed** matters, or when one answer is not reliable enough and you want a vote.

## 4. Orchestrator and workers

> One call (the **orchestrator**) splits the task into subtasks. **Workers** do the subtasks. A last call **combines** the results.

It looks like a chain, but there is one big difference: you do **not know in advance** how many subtasks there will be. The model decides. Example: "summarize these 5 reports" or "change this code base to use the new API": the number of files or reports depends on the input.

Because the model decides the plan, always **cap** the number of subtasks and **clean** the plan text before you use it.

Use it when the task is **too big for one call** and the parts are not known up front, but each part is simple.

### Step by step: orchestrator-workers (exercise 3)

Let's practise the shape of the third exercise with a different example. A plan text lists chores, one per line, with bullets. Clean it, keep at most `limit` chores, do each one (here "do" means format it), and combine the results into a report. The orchestrator is only a given text, to keep the example small.

1. Split the plan into lines. Remove spaces and leading bullets, skip empty lines.
2. Keep the first `limit` lines.
3. Do each chore.
4. Combine the results into numbered lines.

```python
def clean_lines(text, limit):
    lines = []
    for line in text.splitlines():
        line = line.strip().lstrip("-*• ").strip()
        if line:
            lines.append(line)
    return lines[:limit]

def do_chore(chore):
    return "done: " + chore

def run_chores(plan_text, limit=3):
    chores = clean_lines(plan_text, limit)
    results = [do_chore(chore) for chore in chores]
    report = "\n".join(f"{i}. {result}" for i, result in enumerate(results, start=1))
    return report

print(run_chores("- wash cups\n\n* sweep floor\n- water plants\n- paint wall"))
# -> 1. done: wash cups
#    2. done: sweep floor
#    3. done: water plants
```

The fourth chore was dropped by the limit. Your exercise does the same, with model calls for the plan, for each worker and for the combine step.

## 5. Evaluator and optimizer

> One call writes. A second call **judges**. If it is not good, a third call rewrites with the feedback. Repeat, up to a limit.

It works well when you have **clear quality criteria** and the first draft is rarely good enough: translations, code that must pass tests, a summary that must keep certain facts. The judge can be a model, or plain code (run the tests, check the length).

Two warnings:

- **Always set a hard limit** on the rounds. A judge that is never satisfied loops for ever, and every round costs money.
- Check that the loop **helps**. Compare the final score with and without the loop on your test set. Sometimes the first draft was already as good.

This is also called **reflection** (you meet it again in the next lesson).

### Step by step: an improve loop (exercise 4)

Let's practise the shape of the fourth exercise with a different example, with no model: make a title short enough. The judge checks the length. The reviser drops the last word. The loop has a limit.

1. Evaluate the draft. If it is good, return it, saying how many revisions were used.
2. If the limit is reached, return the draft with `accepted` set to `False`.
3. Otherwise revise and count one more revision. Then evaluate again.

```python
def judge(title, max_len):
    return len(title) <= max_len

def revise(title):
    words = title.split(" ")
    return " ".join(words[:-1])

def shorten_title(title, max_len, max_rounds=3):
    revisions = 0
    while True:
        if judge(title, max_len):
            return {"text": title, "rounds": revisions, "accepted": True}
        if revisions == max_rounds:
            return {"text": title, "rounds": revisions, "accepted": False}
        title = revise(title)
        revisions += 1

print(shorten_title("How to brew good tea at home", 12, max_rounds=4))
# -> {'text': 'How to brew', 'rounds': 4, 'accepted': True}
print(shorten_title("How to brew good tea at home", 5, max_rounds=2))
# -> {'text': 'How to brew good tea', 'rounds': 2, 'accepted': False}
```

Your exercise has the same loop. The judge is a model call that replies `OK` or a feedback sentence, and the reviser is a model call that gets the feedback.

## Choosing a pattern

| The task is... | Use |
| --- | --- |
| A fixed series of steps | **Chain** |
| Different kinds of input, different handling | **Route** |
| Independent parts, or a vote for reliability | **Parallel** |
| Too big for one call, parts decided by the model | **Orchestrator-workers** |
| Needs polishing against clear criteria | **Evaluator-optimizer** |
| Unknown steps that depend on tool results | An **agent** (lesson 1) |

Patterns combine. A common one: **route** to a handler, and the handler is a **chain** with a final **improve** step. Start with one call. Add a pattern only when a test shows you need it.

## Try it live

Pick the task *"Write a product description for a water bottle, then check it for claims we cannot prove."*

1. Do it in **one** call. Save the answer.
2. Do it as a **chain**: draft, then a check call that lists claims that cannot be proven, then a rewrite. Compare.
3. Add the **improve loop** with a limit of 2. Count the calls, the tokens (`response.usage`) and the time.
4. Try routing: 3 products of different kinds (a bottle, a phone, a book) with 3 different handler prompts.
5. Write one sentence: which version is worth its cost?

## A little deeper

- **Gates.** A check in plain code between steps (length, valid JSON, a banned word) is cheap and strong. Fail early before you spend more calls.
- **Use different models for different steps.** A small fast model for routing and simple steps, a larger one for hard steps. This is a big cost saver.
- **Orchestrator-workers vs agent.** Both let the model decide the work. But here the code still owns the loop: plan once, run the workers once, combine once. An agent loops until it decides to stop.
- **Workers that see more.** If a worker needs another worker's result, you have a chain inside the workers. Sometimes the answer is two rounds of orchestration.
- **Voting needs variety.** If all votes use temperature 0, they are the same. Use a higher temperature, or different prompts.
- **Error handling.** One failed call in a chain breaks the chain. Add retries (GenAI lesson 6) in `ask`, and decide what a partial result means.
- **Testing.** Because the path is fixed, you can test each step on its own, with a fake client, as the exercises do.

## Common mistakes

- Building an agent when a chain would do.
- A chain with no check between steps, so a bad first step ruins all the rest.
- Trusting the router's output without cleaning it and without a default.
- No limit on the number of subtasks or on the rounds of an improve loop.
- Voting with temperature 0 (every vote is the same).
- Adding patterns without measuring if they help.
- Hiding the intermediate outputs, so you cannot see which step went wrong.

## Interview corner

**Name the common workflow patterns.**
Prompt chaining, routing, parallelization (sectioning and voting), orchestrator-workers, and evaluator-optimizer.

**What is the difference between orchestrator-workers and an agent?**
In orchestrator-workers the code runs a fixed shape: plan once, run the workers, combine. The model decides the subtasks but not the control flow. In an agent the model controls the loop and decides when to stop.

**When would you use routing?**
When inputs are different kinds that need different prompts, tools or models. A cheap classifier call picks the path, and you clean its output and keep a default route.

**What does parallelization save?**
Time, not money. Independent calls run together, so the wait is the slowest call, not the sum. Voting also improves reliability.

**What are the risks of an evaluator-optimizer loop?**
It can loop without end and cost a lot, the judge can be wrong or biased, and the loop may not improve quality. Set a hard limit, use clear criteria, and measure with and without the loop.

## Summary

- Five patterns: **chain**, **route**, **parallel** (sectioning and voting), **orchestrator-workers**, **evaluator-optimizer**.
- A chain feeds each output into the next step. Add gates (cheap checks) between steps.
- A router classifies at temperature 0, cleans the label, and falls back to `"other"`.
- Parallel calls save time (and a vote adds reliability), not money.
- Orchestrator-workers: plan, run one worker per subtask, combine. Cap and clean the plan.
- Evaluator-optimizer: draft, judge, revise, with a hard limit on rounds.
- Start with one call. Add a pattern only when a test shows the need, and measure its cost.
- Reference: `reference/genai-groq.md`.
