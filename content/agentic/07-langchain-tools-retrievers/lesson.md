---
title: "LangChain tools and retrievers, and SDK vs LangChain"
summary: Write tools with @tool, run the model's tool calls, build the agent loop with LangChain messages, build a RAG chain with a retriever, and decide when LangChain is worth it.
plan_ids: []
---

In lesson 6 you built chains: prompt, model, parser. Now you give the model **tools** and **documents**. These are the two things almost every real agent needs.

You already know both ideas. Tool calling is GenAI lesson 11 and the agent loop is GenAI lesson 27. RAG is GenAI level 4. Here you see how the same ideas look in LangChain. At the end we compare it with the plain SDK, so you can answer "why LangChain?" with real reasons.

## Tools with `@tool`

In the Groq SDK you wrote a JSON spec for every tool by hand. In LangChain you write a normal function and add `@tool`:

```python
from langchain_core.tools import tool

@tool
def convert_temp(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32

print(convert_temp.name)
# -> convert_temp
print(convert_temp.description)
# -> Convert a temperature from Celsius to Fahrenheit.
print(convert_temp.args)
# -> {'celsius': {'title': 'Celsius', 'type': 'number'}}
print(convert_temp.invoke({"celsius": 100}))
# -> 212.0
```

What just happened: LangChain read the function name (the tool name), the docstring (the description) and the type hints (the argument types). It built the JSON schema for you. The decorator also made the tool a Runnable, so it has `invoke`.

> **Trap:** the model reads **only** the name, the description and the argument schema. A vague docstring or a missing type hint makes the tool hard to use. This is lesson 2's tool design again.

## Tool calls come back inside the message

You give tools to a model with `bind_tools`:

```python
model_with_tools = model.bind_tools([convert_temp])
reply = model_with_tools.invoke("What is 100 C in F?")
print(reply.tool_calls)
# -> [{'name': 'convert_temp', 'args': {'celsius': 100}, 'id': 'call_1', 'type': 'tool_call'}]
```

(With a real model the `id` looks different. The example output is from a fake model, so you can run it without a key.) If the model wants a tool, `reply.tool_calls` is a list of dicts. If it has a final answer, the list is empty and `reply.content` holds the text.

You run each call and answer with a `ToolMessage` that has the same `tool_call_id`:

```python
from langchain_core.messages import ToolMessage

result = convert_temp.invoke(reply.tool_calls[0]["args"])
tool_message = ToolMessage(content=str(result), tool_call_id=reply.tool_calls[0]["id"])
```

The model uses the id to match your answer to its question. This is the same idea as `tool_call_id` in the Groq SDK.

### Step by step: run the tool calls (exercise 2)

Exercise 2 asks you to run **all** the calls of one message and never crash. A worked example with a different goal: "shout every name in a list of calls".

1. Make a dict from tool name to tool, so you can look a tool up fast.
2. Loop over `ai_message.tool_calls`.
3. For each call: find the tool. If it is missing, make an error text. If it exists, call it inside `try`, and make the result text (or an error text from `except`).
4. Put the text in a `ToolMessage` with the call's id and add it to the result list.
5. Return the list.

The reason to send errors **as messages** is that the model can read "Error: unknown tool" and try something else. If your code crashes, the whole run is lost.

## The agent loop in LangChain

Put the pieces together and you have the loop from lesson 27:

```python
messages = [HumanMessage(question)]
for _ in range(max_steps):
    ai = model_with_tools.invoke(messages)
    messages.append(ai)
    if not ai.tool_calls:
        return ai.content
    messages.extend(run_tool_calls(ai, tools))
```

The `AIMessage` with the tool calls **must** stay in the list before its tool results. Exercise 3 asks you to write this loop and keep the step limit.

LangChain and LangGraph also have a ready-made agent (a "prebuilt" agent) that does this loop for you, with `create_agent` or `create_react_agent`. Names changed between versions, so check the docs of the version you install. Knowing the loop by hand tells you what that helper does inside.

## Documents and retrievers

For RAG, LangChain has two small ideas:

- A **`Document`** has `page_content` (text) and `metadata` (a dict, for example `{"source": "tea.md"}`).
- A **retriever** is a Runnable that takes a question and returns a list of `Document`s.

You can make a retriever from a vector store in one line, for example `vectorstore.as_retriever(search_kwargs={"k": 3})`. In the exercise you write a tiny keyword retriever from a plain function with `RunnableLambda`. Anything that takes a string and returns documents is a retriever.

## A RAG chain

```python
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

chain = (
    {"context": retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()}
    | prompt | model | StrOutputParser()
)
print(chain.invoke("Where does tea grow?"))
# -> Tea grows in Assam.   (from a fake model)
```

Read it from left to right:

1. The dict runs two branches on the same question. `retriever | format_docs` makes the context text. `RunnablePassthrough()` passes the question as it is.
2. The prompt fills `{context}` and `{question}`.
3. The model answers and the parser makes a string.

This is the RAG pipeline of GenAI lesson 21 in 4 lines. Citations, reranking and checking are extra steps you can add as more pieces in the chain.

### Step by step: build a retriever (exercise 4)

1. Take the question and make a set of lowercase words.
2. For each document, count how many of those words are in the document's words.
3. Keep the documents with a score above 0.
4. Sort by score, highest first. Python's `sort` keeps the order of equal items.
5. Return the first `k`. Wrap the function with `RunnableLambda` so it becomes a Runnable.

## SDK or LangChain?

| Question | Plain SDK (Groq) | LangChain |
|---|---|---|
| Swap provider | rewrite the calls | change one class |
| Prompt, parser, retry | write your own | ready, shared methods |
| Tracing and logs | add them yourself | LangSmith works with no code change |
| Debugging | you see every call | extra layers to read |
| Learning cost | low | medium, and names change often |
| Best for | one call, a small service, full control | many steps, many models, a team |

A common pattern in industry: use the SDK for small, hot paths where you want control, and LangChain or LangGraph for larger flows where reuse and tracing pay off. Say this in an interview. It shows judgment, not loyalty.

## Try it live

1. In your own folder: `uv add langchain-groq langchain-core`. Set `GROQ_API_KEY`.
2. Write the `convert_temp` tool and a second tool of your own. Run `ChatGroq(...).bind_tools([...])` and print `reply.tool_calls` for three questions.
3. Ask a question that needs no tool. What is in `tool_calls`? What is in `content`?
4. Run the full loop from this lesson with a real model.
5. Make 5 `Document`s about your own notes, use your keyword retriever, and ask a question with the RAG chain. Then ask something that is not in the documents.

## A little deeper

- **`@tool` with Pydantic.** For complex arguments use `@tool(args_schema=MySchema)` with a Pydantic class, so you can add field descriptions and limits.
- **Parallel tool calls.** A message can hold several calls. Exercise 2 handles this because it loops over the list.
- **`ToolNode` in LangGraph.** LangGraph has a ready node that runs `tool_calls` for you. It does what exercise 2 does, with extra error handling. You see it in lesson 8.
- **Vector store retrievers.** `Chroma`, `FAISS` and others have `as_retriever()`. The interface is always the same: string in, `Document`s out.
- **Where LangChain hides things.** The prompt that reaches the model is built from templates and messages. If an answer looks wrong, print the prompt (`prompt.invoke(...)`) first, as in the exercises.

## Common mistakes

- A tool without a docstring or type hints. The model cannot use it well.
- Forgetting the `tool_call_id`, or not adding the `AIMessage` before the `ToolMessage`s.
- Letting a tool error crash the loop, instead of returning it as a message.
- No step limit in the loop.
- Putting a huge retrieved text in the context with no limit.
- Treating LangChain as required. For a plain call, the SDK is simpler.

## Interview corner

**How does LangChain turn a Python function into a tool?**
`@tool` reads the name, docstring and type hints and builds a JSON schema. The model sees only that schema, so descriptions matter.

**What is the message flow when a model calls a tool?**
The `AIMessage` has `tool_calls`. You run them and add a `ToolMessage` per call with the same `tool_call_id`. Then you call the model again with the whole list.

**What is a retriever in LangChain?**
A Runnable: question string in, list of `Document`s out. A vector store, a BM25 index or your own function can all be one.

**Write a RAG chain in LCEL.**
`{"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | model | StrOutputParser()`.

**Why not always use LangChain?**
It adds a layer to learn, debug and keep up with as names change. For a single call or full control, the SDK is better. For many steps, many models or a team, the shared parts pay off.

## Summary

- `@tool` turns a function into a tool. Name, docstring and type hints become the schema the model sees.
- `model.bind_tools(tools)`: the reply may have `tool_calls`. Answer each with a `ToolMessage` that has the same id.
- Send tool errors back as messages. Always keep a step limit.
- A **retriever** is a Runnable: string in, `Document`s out. A **RAG chain** joins retriever, prompt and model with `|`.
- Pick the SDK for small, controlled paths and LangChain for bigger, reusable flows.
- Reference: `reference/agentic-langchain-langgraph.md`.
