# Agentic AI: LangChain, LangGraph, MCP, safety, evals, design

Short entries for the Agentic AI track, levels A2 to A4 (lessons 06 to 20). Level A1 (plain-Python patterns) is in `genai-groq.md`, section "Agentic patterns". Library names and signatures change often. They are written from memory and checked against the versions in `pyproject.toml` where an example was run. **Check the official docs for your version.**

## LangChain basics (agentic 06)
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

chain = ChatPromptTemplate.from_template("Explain {topic} in one line.") | ChatGroq(model="qwen/qwen3.8-27b") | StrOutputParser()
chain.invoke({"topic": "tokens"})        # one call. Also .batch([...]) and .stream({...})
```
**Theory:** a *Runnable* has `invoke`, `batch` and `stream`. `a | b` makes a new Runnable that feeds the output of `a` into `b` (LCEL). `RunnableLambda(fn)` wraps your function. A dict of Runnables runs them in parallel. `.with_retry()` and `.with_fallbacks([...])` add safety.
**Gotcha:** a prompt needs a dict, a parser needs the model message. Double the braces (`{{`) to write a real brace in a template. Skip LangChain for a single call.

## Tools and retrievers (agentic 07)
```python
from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

model = model.bind_tools([add])
reply = model.invoke("2 + 3?")           # reply.tool_calls -> [{"name": "add", "args": {...}, "id": "..."}]
# answer each call: ToolMessage(content="5", tool_call_id=call["id"])
```
**Theory:** the name, the docstring and the type hints become the schema the model reads. A *retriever* is a Runnable: a string in, a list of `Document`s out. A RAG chain is `retriever | format | prompt | model | parser`.
**Gotcha:** every tool call needs a `ToolMessage` with the **same id**. Always keep a step limit.

## LangGraph state, nodes, edges (agentic 08)
```python
from typing import Annotated, TypedDict
from operator import add
from langgraph.graph import END, START, StateGraph

class State(TypedDict):
    n: int
    log: Annotated[list, add]            # a reducer: new values are appended

def bump(state):
    return {"n": state["n"] + 1, "log": ["bump"]}

graph = StateGraph(State)
graph.add_node("bump", bump)
graph.add_edge(START, "bump")
graph.add_conditional_edges("bump", lambda s: "bump" if s["n"] < 3 else "end", {"bump": "bump", "end": END})
app = graph.compile()
app.invoke({"n": 0, "log": []})          # -> {'n': 3, 'log': ['bump', 'bump', 'bump']}
```
**Theory:** state is a dict, a node returns **only the keys it changes**, an edge picks the next node. No reducer means "replace". `add` appends lists, `add_messages` (from `langgraph.graph.message`) merges chat messages by id.
**Gotcha:** a loop needs a counter in the state. `recursion_limit` (in the config) is the last wall, not the plan.

## Checkpointer, threads, streaming, time travel (agentic 09)
```python
from langgraph.checkpoint.memory import InMemorySaver

app = graph.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "user-1"}}
app.invoke({"n": 0, "log": []}, config)
app.get_state(config).values             # the saved state
list(app.get_state_history(config))      # checkpoints, newest first
app.invoke(None, config)                 # None = continue or replay from the saved state
for update in app.stream(inputs, config, stream_mode="updates"): ...   # also "messages" and "values"
```
**Theory:** a checkpointer saves the state after each step under a `thread_id`. That is short-term memory: send only the **new** input on the next turn. `update_state` plus `invoke(None, ...)` forks from a past point.
**Gotcha:** `InMemorySaver` is for tests. Use a database saver in production and delete a thread on request.

## Human in the loop, parallel branches, subgraphs (agentic 10)
```python
from langgraph.types import Command, interrupt, Send

def approve(state):
    answer = interrupt({"question": "Send it?"})   # pauses here, state is saved
    return {"ok": answer == "yes"}

app.invoke(inputs, config)                         # stops at the interrupt
app.invoke(Command(resume="yes"), config)          # continues, answer is the return value
# fan-out: return [Send("worker", {"item": x}) for x in items] from a conditional edge
```
**Theory:** `interrupt` needs a checkpointer and a `thread_id`. Branches that write the same key need a reducer. A compiled graph can be a node (a subgraph).
**Gotcha:** the node **restarts from its first line** on resume, so do no side effects before `interrupt`.

## Memory and context engineering (agentic 11)
```python
facts = recall(store, user_id, question)                       # select: only matching facts
context = build_context(system, store, user_id, history, question, max_chars)   # fixed order, fits a budget
```
**Theory:** the model has no memory. Short-term = the thread. Long-term = a per-user store. Four moves: **write, select, compress, isolate**. Compress old chat into a summary and keep recent messages word for word.
**Gotcha:** never drop the system prompt or the current question. Treat memory as personal data: show it, delete it, no secrets.

## Agentic RAG (agentic 12, project step 21)
```python
graph.add_conditional_edges("grade", decide_next, {"answer": "answer", "rewrite": "rewrite", "give_up": "give_up"})
graph.add_edge("rewrite", "retrieve")      # the loop
```
**Theory:** grade the chunks, then decide: answer, rewrite the question and search again, or give up. `decide_next` is a plain function, so it is easy to test. `stream_mode="updates"` gives the **path** of nodes.
**Gotcha:** the loop needs `max_tries` in the state. "I could not find this" is a good answer. Add a decision only if your eval shows it helps.

## Multi-agent (agentic 13)
```python
return Command(goto="writer", update={"notes": notes})      # handoff: a node names the next node
```
**Theory:** an agent = system prompt + tools + a model loop. *Supervisor*: a central agent names the next worker or `FINISH` (parse the reply strictly, cap the steps). *Handoff*: no boss, a node returns `Command(goto=..., update=...)`.
**Gotcha:** it costs more tokens and is harder to debug. Start with one agent or a workflow.

## MCP, the Model Context Protocol (agentic 14)
```python
from mcp.server.mcpserver import MCPServer      # v2 name. In v1 it was mcp.server.fastmcp.FastMCP
from mcp.client import Client

server = MCPServer("demo")

@server.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

async with Client(server) as client:
    await client.list_tools()                   # -> a tool called "add"
    await client.call_tool("add", {"a": 2, "b": 3})   # content[0].text -> "5"
```
**Theory:** messages are JSON-RPC 2.0. The flow is `initialize`, `initialized`, `tools/list`, `tools/call`. A failing tool returns a result with `isError: true`. An unknown method is a protocol error. Transports: stdio and Streamable HTTP.
**Gotcha:** tool names, descriptions and results are text in the prompt, so a bad server can inject instructions. Trust only reviewed servers. Check the SDK version.

## Agent safety (agentic 15)
```python
result = run_tool_safely(call, registry, table, approve, audit, limits)   # one guarded door for every tool call
```
**Theory:** quarantine tool output (scan, label as untrusted, cut). Least privilege: unknown tool means no. Risk tiers: low runs, medium runs under limits, high needs a person. Break the **lethal trifecta**: private data + untrusted input + a way out. Add step and cost caps, argument validation, and an audit log.
**Gotcha:** no layer is perfect. Put limits in code, not only in the prompt.

## Agent evals and tracing (agentic 16, project step 23)
```python
trace = []
traced_call(trace, "search", "tool", time.perf_counter, search, query)   # adds a span, even on failure
trace_summary(trace)                      # spans, total_ms, llm_calls, tool_calls, tokens, errors
trajectory_match(["a", "x", "b"], ["a", "b"], "in_order")   # True. Modes: exact, in_order, any_order
gate(baseline_results, new_results)       # {"ok": False, "reasons": [...]} blocks a worse change
```
**Theory:** a *span* is one step (name, kind, ms, tokens, error). Evaluate the answer, the **trajectory** (which tools, in what order) and the efficiency (steps, tokens, time). A regression gate blocks a drop in pass rate, any case that passed before and fails now, and a big cost growth. Langfuse, LangSmith, Phoenix and OpenTelemetry store and show traces (names from memory, check the docs).
**Gotcha:** record the span when a call fails, then raise the error again. Redact private data from traces. A crash in one eval case must not stop the run.

## LLM system design (agentic 17)
```python
cost = input_tokens / 1_000_000 * input_price + output_tokens / 1_000_000 * output_price
servers = math.ceil(requests_per_second * tokens_per_request / tokens_per_second_per_server * headroom)
```
**Theory:** method: **clarify, estimate, design simply, go deep, measure**. Input tokens and agent history dominate cost. Latency: independent steps run in parallel, dependent steps add up, so work on the critical path and watch p95. A response cache skips the model. A prompt cache makes a stable prefix cheaper.
**Gotcha:** never share cached answers across permission boundaries. For hosted APIs, plan for rate limits.

## The capstone (agentic 18, project step 26)
```python
out = answer_question(client, question, tools, [], time.perf_counter)   # guard, route, tool, answer, trace
format_report(capstone_report(run_cases(client, cases, tools)))        # six lines for your README
```
**Theory:** route with a cheap call and a strict parse (unclear means the harmless route). Wrap tool output as untrusted. A failing tool gives a polite message and no made-up answer. The report: cases, pass rate, average steps, tokens, p95 latency, failed ids.
**Gotcha:** build plain RAG and record a **baseline first**. Without it you cannot say that anything improved.

## Mock interviews (agentic 19 and 20)
```python
allow(bucket, now, cost=1)      # token bucket: refill by elapsed time, never above capacity
shard_for(tenant_id, n)         # md5(tenant) % n: stable, but changing n moves many tenants
```
**Theory:** answer first, then the reason, then an example or a trade-off. Design method: clarify, estimate, draw simply, go deep, measure. Rate limits: token bucket (bursts allowed) or sliding window (strict). Health: p95 latency and error rate against targets.
**Gotcha:** use consistent hashing or a lookup table when the number of shards changes. Say what you would not build yet.
