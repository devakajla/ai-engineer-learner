---
title: "Multi-agent systems: supervisor, handoff and when not to"
summary: Split a job between worker agents with a supervisor or with handoffs, build both in LangGraph, and learn why one agent is often better.
plan_ids: []
---

One agent with ten tools and a long prompt gets confused. A tempting fix is to split the job: a **researcher**, a **writer**, a **reviewer**, each a separate agent. This is a **multi-agent system**.

Be careful. More agents means more model calls, more cost, more latency and more ways to fail. Many problems that look like they need a team are solved by **one agent with good tools** or by a plain **workflow** (lesson 3). This lesson shows how multi-agent works, so you can also say when **not** to use it.

## What an agent really is

No magic. An agent is:

```
system prompt  +  (maybe) its own tools  +  a loop that calls the model
```

A "researcher agent" is a system prompt that says "you find facts" and maybe a search tool. A "writer agent" is a different prompt and no tools. Splitting agents means splitting **prompts, tools and context** so each part is small and focused.

```python
workers = {
    "researcher": {"description": "finds facts", "system": "You are a researcher."},
    "writer": {"description": "writes the final text", "system": "You are a writer."},
}
```

### Step by step: one worker (exercise 1)

1. Take the task as the prompt.
2. If other workers already produced something, add it as "Work so far".
3. Call the model with the worker's own system prompt.
4. Return the worker's name with its output, so the next step knows who said what.

## Pattern 1: the supervisor

One **supervisor** agent decides who works next. It does not do the work.

```
          +--> researcher --+
task --> supervisor <-------+
          +--> writer ------+
          +--> FINISH -> answer
```

After each worker finishes, control returns to the supervisor. It reads the work so far and picks the next worker, or says `FINISH`.

The supervisor's prompt lists the workers and what they do, the task, and the work so far. Its reply must be **one word**. You parse it strictly: an exact worker name or `FINISH`, anything else is "unknown" (exercise 2). Never guess. A wrong guess sends work to the wrong agent.

You can write the loop in plain Python first (exercise 3):

```python
for _ in range(max_steps):
    choice = parse_choice(ask(client, supervisor_prompt(task, workers, results)), list(workers))
    if choice == "FINISH": break
    results.append(run_worker(client, choice, workers[choice], task, format_results(results)))
```

What just happened: ask the supervisor, run its choice, store the result, repeat. `max_steps` stops a supervisor that never says FINISH. It is also your **cost cap**: each step is at least two model calls.

## The same thing as a graph

In LangGraph the supervisor is a node. Each worker is a node with an edge back to the supervisor. A conditional edge chooses the next worker (lesson 8):

```python
graph.add_edge(START, "supervisor")
for name in workers:
    graph.add_node(name, make_worker_node(name))
    graph.add_edge(name, "supervisor")
graph.add_conditional_edges("supervisor", route, {**{n: n for n in workers}, "FINISH": END})
```

The workers' results are collected in a state key with an `add` reducer (lesson 8), so each worker adds to the list.

The graph version gives you what plain Python does not: streaming of each step, a checkpointer (lesson 9), human approval before a worker (lesson 10), and tracing (lesson 16). That is the real reason to use a framework.

## Pattern 2: handoff

Here no boss exists. An agent finishes its part and **hands off** to the next one. In LangGraph a node returns a `Command`:

```python
from langgraph.types import Command

def researcher(state):
    return Command(goto="writer", update={"notes": "facts about " + state["topic"]})
```

`goto` is the next node. `update` changes the state at the same time. You need no edge from `researcher` to `writer`. The control flow is **inside the node**, so a node can decide at run time where to go.

```python
app.invoke({"topic": "RAG", "notes": "", "draft": ""})
# -> {'topic': 'RAG', 'notes': 'facts about RAG', 'draft': 'Report: facts about RAG'}
```

| | Supervisor | Handoff |
|---|---|---|
| Who decides | one central agent | each agent decides who is next |
| Easy to see the flow | yes, one place | no, spread over nodes |
| Extra model calls | one per step | none for routing |
| Good for | a team with a clear lead | a fixed pipeline, a customer-support triage (billing, tech, sales) |

## Other shapes you will see

- **Hierarchy:** supervisors of supervisors. Each team is a subgraph (lesson 10).
- **Network:** any agent can call any other. Hard to control. Avoid it at first.
- **Agent as a tool:** a main agent calls a sub-agent like a function and gets text back. Simple, and the sub-agent has its own small context (the "isolate" move of lesson 11).
- **Debate / critic:** one agent writes, another criticises (the evaluator-optimizer of lesson 3).

Frameworks such as CrewAI, AutoGen and the OpenAI Agents SDK package these shapes (lesson 5; check each project's docs for the current names).

## When NOT to use multi-agent

Ask these first:

1. **Can one agent with better tools do it?** Often yes.
2. **Is it a fixed chain?** Then it is a **workflow**: plain code calling the model in order. Cheaper and easier to debug.
3. **Do the steps depend on each other a lot?** Agents that need the same context fight over it. Passing text between them loses detail.
4. **Can you afford it?** A team can use 5 to 15 times the tokens of one agent.

Use multiple agents when the parts have **different tools, different permissions or different context** (for example, a "payments agent" that is the only one allowed to touch money), or when parts can run **in parallel**.

> **Rule of thumb.** Start with a single agent. Add an agent only when you can point to a failure that the split fixes, and measure that it did (lesson 16).

## Try it live

1. Make three workers with real prompts: `researcher` (uses a tiny list of facts), `writer`, `reviewer`.
2. Run `supervise(...)` with the real Groq model on "Explain what RAG is in 3 sentences".
3. Print each supervisor reply. Does it always answer with one clean word? Try a weaker prompt and watch it break.
4. Build the same job as **one** prompt to one agent. Compare the quality, the number of calls and the time.
5. Build the handoff graph and print the stream names.

## A little deeper

- **Context per agent.** The big win of multi-agent is a small context for each agent. Pass **summaries or results**, not whole chats.
- **Parallel workers.** Use `Send` (lesson 10) to run several workers at once, and a reducer to collect results.
- **Parent commands.** A node inside a subgraph can send control to a node of the parent with `Command(graph=Command.PARENT, ...)` (check the docs).
- **Failure spreads.** One agent's mistake becomes the next agent's input. Check outputs between steps.
- **Typed hand-offs.** Pass structured data (a Pydantic object, GenAI lesson 10) between agents, not free text.
- **Loops.** Two agents can bounce work back and forth for ever. Keep a step cap and a cost cap.
- **Prompt-injection spread.** A worker that reads a web page can pass a hidden instruction to the next worker (lesson 15).

## Common mistakes

- Using a team when one agent would do.
- A supervisor that guesses the worker name from a messy reply.
- No `max_steps`. The loop runs and bills for ever.
- Passing whole conversations between agents.
- Giving every agent every tool. Least privilege matters more with many agents.
- Not logging which agent said what.
- Never comparing with a single-agent baseline.

## Interview corner

**What is a multi-agent system?**
Several agents (each a prompt, maybe tools, and a model loop) that share one job. Common shapes are supervisor, handoff, hierarchy and agent-as-tool.

**Supervisor vs handoff?**
A supervisor routes every step centrally: easy to follow, one extra model call per step. In a handoff each agent passes control directly (`Command(goto=...)`): no routing calls, but the flow is spread over the nodes.

**When would you avoid multi-agent?**
When one agent with good tools, or a fixed workflow, solves it. Multi-agent costs more tokens, adds latency, and makes failures harder to trace.

**How do you keep a multi-agent system under control?**
Step caps, cost caps, least-privilege tools per agent, typed hand-offs, tracing of every agent step, and an eval against a single-agent baseline.

**Why split into agents at all?**
For small focused contexts, separate tools and permissions, parallel work, and easier testing of each part.

## Summary

- An agent = system prompt + tools + a model loop. A multi-agent system splits prompts, tools and context.
- **Supervisor:** a central agent names the next worker or `FINISH`. Parse its reply strictly. Cap the steps.
- **Handoff:** a node returns `Command(goto=..., update=...)`. No boss, no routing call.
- In LangGraph, workers are nodes with edges back to the supervisor, and results collect with a reducer.
- Multi-agent costs more. Start with one agent or a workflow, and split only when you can show it helps.
- Use separate agents for different tools, permissions or context.
- Reference: `reference/agentic-langchain-langgraph.md`.
