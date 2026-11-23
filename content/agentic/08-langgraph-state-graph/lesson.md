---
title: "LangGraph: state, nodes, edges, reducers and routing"
summary: Learn to draw an agent as a graph - a shared state, nodes that change it, edges that pick the next step - and build chains, routers and loops with LangGraph.
plan_ids: []
---

In lessons 3 and 4 you wrote workflows and agent loops as Python code: `for`, `while`, `if`. That works, but when the flow grows (branches, loops, retries, waiting for a human) the code gets hard to read, test and change.

**LangGraph** asks you to draw the flow instead. You say what the **steps** are and which step can come **after** which. LangGraph runs it. It gives you, for free, things that are hard to write by hand: saving progress, resuming, streaming, pausing for a human. You use those in lessons 9 and 10.

LangGraph is the framework most job posts mean when they say "agent framework". It is made by the LangChain team but it works alone. You do not need a chain to use it.

> **Setup.** `langgraph` is already installed in the Learner project. In your own folder: `uv add langgraph langchain-core`.

## Three words: state, node, edge

Think of a **relay race**. A baton goes from runner to runner.

- **State** is the baton: one dict that every step can read.
- **Node** is a runner: a Python function. It gets the state and returns **only the keys it wants to change**.
- **Edge** is the track: it says which node runs next.

Two special points: `START` (where the baton begins) and `END` (where the race ends).

## A first graph

```python
from operator import add
from typing import Annotated, TypedDict
from langgraph.graph import END, START, StateGraph

class State(TypedDict):
    text: str
    steps: Annotated[list, add]

def clean(state):
    return {"text": state["text"].strip(), "steps": ["clean"]}

def shout(state):
    return {"text": state["text"].upper() + "!", "steps": ["shout"]}

graph = StateGraph(State)
graph.add_node("clean", clean)
graph.add_node("shout", shout)
graph.add_edge(START, "clean")
graph.add_edge("clean", "shout")
graph.add_edge("shout", END)
app = graph.compile()

print(app.invoke({"text": "  hello ", "steps": []}))
# -> {'text': 'HELLO!', 'steps': ['clean', 'shout']}
```

> `class State(TypedDict)` is a class. Copy this shape for now. You learn classes in Python lesson 19. A `TypedDict` is only a dict with named keys that tools can check.

What just happened:

1. `StateGraph(State)` makes an empty graph that knows the shape of the state.
2. `add_node("clean", clean)` registers a function under a name.
3. `add_edge(a, b)` says "after `a`, run `b`".
4. `compile()` checks the graph (for example, no missing nodes) and gives you a runnable app.
5. `invoke` runs it from `START` and returns the final state. Like a chain it also has `stream` and `batch`.

To **see** the graph as a picture, use `app.get_graph().draw_mermaid()`. It prints text you can paste into a Mermaid viewer.

### Step by step: build a graph (exercise 1)

Exercise 1 is this graph again. The same steps for a new job, "add 1, then double":

1. Write the state: `n: int` and a `steps` list with the `add` reducer.
2. Write one function per step. Each returns only what changed.
3. Make `StateGraph(State)`, add each function with a name.
4. Draw the edges in order: `START` to the first node, each node to the next, the last to `END`.
5. `compile()` and return the app. You never call the nodes yourself. The graph calls them.

## Reducers: what happens when a node returns a key

A node returns `{"steps": ["clean"]}`. What happens to the old `steps`? The state key decides:

- **No reducer:** the new value **replaces** the old one.
- **A reducer** (the second part of `Annotated[...]`): the reducer **combines** the old and the new value. `operator.add` on lists means "append".

```python
class T(TypedDict):
    a: int
    b: Annotated[list, add]

# node 1 returns {"a": 1, "b": ["x"]}, node 2 returns {"a": 2, "b": ["y"]}
# start {"a": 0, "b": []}
# -> {'a': 2, 'b': ['x', 'y']}
```

`a` was replaced. `b` collected both values. For chat history LangGraph has a ready reducer, `add_messages`. It appends messages, and if a message has the same id as an old one, it replaces it:

```python
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
```

This `messages` state is in almost every LangGraph agent. In exercise 4 you build the smallest chat graph.

> **Why reducers matter.** In lesson 10 several nodes run **at the same time** and all write to the same key. Without a reducer the result would depend on who finishes last. A reducer makes it safe.

## Conditional edges: routing

A normal edge always goes to the same node. A **conditional edge** calls a function to choose. This is the routing pattern from lesson 3:

```python
def pick_route(state):
    return state["route"]            # returns a label

graph.add_conditional_edges("classify", pick_route, {"math": "math", "chat": "chat"})
```

The function returns a label. The dict maps each label to a node name. (A label can be `END`.) Only the chosen node runs.

### Step by step: a router (exercise 2)

1. A first node reads the input and writes a `route` into the state (`"math"` or `"chat"`).
2. A small function reads `state["route"]` and returns it.
3. `add_conditional_edges("classify", that_function, {...})` joins them.
4. Each handler node goes to `END`.

Keep the **decision** (which route) in one node and the **choice** (which edge) in a tiny function. Both are then easy to test.

## Loops

An edge can go back to an earlier node. A conditional edge decides whether to loop:

```python
graph.add_conditional_edges("attempt", should_stop, {"again": "attempt", "stop": END})
```

This is how the agent loop looks as a graph: `agent -> tools -> agent -> ... -> END`. Every loop needs a way out, so keep a counter in the state. As a second guard, LangGraph stops after 25 steps by default and raises `GraphRecursionError`. You can change it per call: `app.invoke(state, {"recursion_limit": 10})`.

```python
# a loop with no way out, and recursion_limit 5:
# -> GraphRecursionError: Recursion limit of 5 reached without hitting a stop condition.
```

## An agent as a graph

Now you can draw lesson 7's agent loop:

```
START -> agent --(tool calls?)--> tools -> agent
                 \--(no)--------> END
```

- `agent` is a node that calls the model with the `messages` state.
- `tools` runs the tool calls. LangGraph has a ready node, `ToolNode(tools)`, from `langgraph.prebuilt`.
- A ready function, `tools_condition`, returns `"tools"` or `END` by looking at the last message.

You write the loop in lesson 9 with memory and in lesson 12 for agentic RAG. First, make sure the small graphs are clear.

## Try it live

1. Build the chat graph from exercise 4 with `ChatGroq`. Call it with `{"messages": [HumanMessage("Hi, I am Dev")]}` and print the messages.
2. Call it again with a new input that does **not** include the old messages. Does it remember? (No. State lives only inside one run. Lesson 9 fixes this.)
3. Print `app.get_graph().draw_mermaid()` for your router graph. Paste it into a Mermaid viewer.
4. Make the retry loop run forever on purpose. Read the error.
5. Add a `print` inside each node and watch the order.

## A little deeper

- **Nodes can return `Command`.** `Command(update={...}, goto="name")` lets a node change the state **and** choose the next node, so you need no conditional edge. You use it for handoffs in lesson 13.
- **Input and output schemas.** A graph can take a smaller input than its state and return a smaller output (`StateGraph(State, input_schema=..., output_schema=...)`).
- **Node caching and retries.** Nodes can have a retry policy, so a flaky API call retries without a loop in your graph.
- **Sync and async.** Nodes can be `async def`. Use `app.ainvoke` and `app.astream` in a web server.
- **Graph or plain code?** If the flow is a short fixed chain, plain code is simpler. Use a graph when you need loops, branches, saved progress, human approval or streaming.

## Common mistakes

- Returning the **whole** state from a node. Return only the changes.
- Forgetting a reducer, so a list is replaced and not appended.
- Returning `{"messages": reply}` instead of `{"messages": [reply]}` for a list state.
- A loop with no counter and no exit edge.
- A label from the routing function that is missing in the mapping dict.
- Mutating the state in place (`state["x"].append(...)`). Return an update instead.

## Interview corner

**What are state, nodes and edges in LangGraph?**
State is a shared typed dict. Nodes are functions that read it and return updates. Edges say which node runs next, fixed or chosen by a function.

**What is a reducer and why does it matter?**
It says how a returned value combines with the old value of a key (append, merge, replace). It makes updates safe when several nodes write the same key. `add_messages` is the standard one for chat history.

**How do you build a loop in LangGraph?**
A conditional edge that goes back to an earlier node, plus a counter or a stop condition in the state. LangGraph also has a recursion limit as a safety net.

**Why use LangGraph instead of a `while` loop?**
For saved progress (checkpoints), resuming, human approval, streaming, time travel and a clear picture of the flow. For a short fixed chain, plain code is fine.

**What does `compile()` do?**
It checks the graph is well formed and returns a runnable app. You can pass a checkpointer to it (lesson 9).

## Summary

- A graph = **state** (dict) + **nodes** (functions that return changes) + **edges** (next step). `START` and `END` are the ends.
- `compile()` gives an app with `invoke`, `stream` and `batch`.
- A **reducer** combines old and new values: `add` appends lists, `add_messages` handles chat messages. No reducer means replace.
- `add_conditional_edges(node, function, mapping)` routes. Loops are edges that go back, with a counter and a recursion limit.
- Keep the decision (a node) apart from the choice (a small function).
- Use a graph for loops, branches, saved progress, human approval and streaming.
- Reference: `reference/agentic-langchain-langgraph.md`.
