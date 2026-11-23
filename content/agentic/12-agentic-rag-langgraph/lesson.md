---
title: "Agentic RAG in LangGraph"
summary: Turn a one-shot RAG pipeline into a graph that grades what it found, rewrites the question and searches again, and gives up honestly when the documents cannot help.
plan_ids: []
---

Plain RAG (GenAI lesson 21) is a straight line: search, stuff the chunks into a prompt, answer. If the search finds nothing useful, the model still answers, often with a confident guess. That is the most common RAG failure (GenAI lesson 24).

**Agentic RAG** puts **decisions** into the line. The system looks at what it found and chooses what to do next. LangGraph is a good fit, because decisions and loops are exactly what graphs are for (lesson 8).

```
START -> retrieve -> grade --(relevant docs)--> answer -> END
                       |--(none, tries left)--> rewrite -> retrieve   (loop)
                       |--(none, no tries)----> give_up -> END
```

Three new ideas, one per section below: **grade**, **decide**, **loop with a limit**.

## Grade what you found

A **grader** asks a model one small question about each chunk: "is this relevant to the question? yes or no". This is the LLM-as-judge idea of GenAI lesson 41, used inside the app, not only in tests.

```python
def grade_doc(client, question, doc):
    reply = ask(client, f"Question: {question}\n\nDocument: {doc}\n\n"
                        "Is the document relevant to the question? Answer yes or no.")
    return reply.strip().lower().startswith("yes")
```

What just happened: the model gets one chunk and one question. Only a clear `yes` keeps the chunk. A `maybe` or an empty reply counts as `no`, because a wrong chunk in the prompt does more harm than a missing one.

```python
grade_docs(client, "refund time?", ["Refund takes 5 days", "Cats sleep a lot"])
# -> ['Refund takes 5 days']
```

> **Cost.** One model call per chunk. Use a small, fast model for grading, and grade only the top 3 to 5 chunks.

### Step by step: the grader (exercise 1)

1. Build the prompt with the question and one document.
2. Call the model with temperature 0 so the grade is stable.
3. Lower-case the reply, trim it, check `startswith("yes")`.
4. Loop over the docs and keep the `True` ones, in order.

## Decide what to do next

After grading there are three cases:

| Situation | Action |
|---|---|
| some chunks are relevant | **answer** |
| none are relevant and you may still retry | **rewrite** the question, then retrieve again |
| none are relevant and no tries are left | **give up**, say so |

Put this in a small plain function:

```python
def decide_next(state):
    if state["relevant"]:
        return "answer"
    if state["tries"] >= state["max_tries"]:
        return "give_up"
    return "rewrite"
```

In LangGraph this function is the **router** of a conditional edge (lesson 8). It reads the state and returns a label. Keeping it plain makes it easy to test.

**Why rewrite?** Users type short, vague questions ("refunds?"). A model can turn them into a better search query ("How many days does a refund take?"). You met this as query rewriting in GenAI lesson 23.

**Why give up?** "I could not find this in the documents" is a **good** answer. It is much better than a made-up one. Users and auditors trust a system that says it does not know.

## The graph

```python
graph = StateGraph(RagState)
graph.add_node("retrieve", retrieve)
graph.add_node("grade", grade)
graph.add_node("rewrite", rewrite)
graph.add_node("answer", answer)
graph.add_node("give_up", give_up)
graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "grade")
graph.add_conditional_edges("grade", decide_next,
    {"answer": "answer", "rewrite": "rewrite", "give_up": "give_up"})
graph.add_edge("rewrite", "retrieve")      # the loop
graph.add_edge("answer", END)
graph.add_edge("give_up", END)
app = graph.compile()
```

The state carries everything the nodes share: `question`, `docs`, `relevant`, `tries`, `max_tries`, `answer`. Each node returns only the keys it changes.

The nodes use `client` and `search` from the function that builds the graph (a small closure: an inner function that remembers outer variables; you meet closures in Python lesson 23). If that is new, just copy the shape: define the nodes inside `build_rag_graph(client, search)`.

> **Two safety nets against endless loops.** Your own `max_tries` stops the loop in a friendly way (the `give_up` node). LangGraph's `recursion_limit` (lesson 8) is the last-resort wall: it raises `GraphRecursionError`. Use both.

### Step by step: build and run (exercises 3 and 4)

1. Write each node as a tiny function that returns a partial state update.
2. Add the nodes, then the edges. Mark the conditional edge with `decide_next`.
3. `retrieve` adds 1 to `tries` each time. This is what the router counts.
4. Stream with `stream_mode="updates"` and collect the node names. That list is the **path**.
5. Test three paths with a fake model: direct hit, rewrite then answer, give up.

```python
run_rag(app, "refunds")
# -> {'answer': '5 days', 'tries': 2,
#     'path': ['retrieve', 'grade', 'rewrite', 'retrieve', 'grade', 'answer']}
```

## What else makes RAG "agentic"

The graph above is the smallest useful version. More decisions you can add as nodes:

- **Route first.** A router decides: answer from the docs, answer from a web search, or just chat (no retrieval at all). Greetings do not need a vector search.
- **Check the answer.** After answering, a grader asks: is every claim supported by the chunks? If not, retry (this is the self-check of CRAG and Self-RAG, awareness level).
- **Split the question.** "Compare plan A and plan B" becomes two searches (use `Send`, lesson 10).
- **Tool choice.** The agent picks between the vector index, a SQL tool and an API (lesson 7).

Each added decision costs more model calls and more time. Add one only when you can show it fixes real failures with your eval set (GenAI lessons 25 and 41).

## Try it live

1. Use your Chroma index from GenAI lesson 17 (or a list of 5 small texts) as `search`.
2. Use the real Groq client. Ask a question the docs can answer, then one they cannot ("Who won the cricket world cup?").
3. Print the `path` for both. The second should end in `give_up`.
4. Ask a vague question ("refunds?"). Print the rewritten question from the state.
5. Time both runs. Note how many model calls each needed. This is the price of the extra checks.

## A little deeper

- **Grade in one call.** Instead of one call per chunk, send all chunks and ask for the numbers of the relevant ones as JSON. Cheaper, but a bit less reliable.
- **Score, not yes/no.** A 0 to 1 relevance score lets you set a threshold. It also adds noise.
- **Rewrite history.** Remember earlier rewrites. Do not try the same query twice.
- **Fallback sources.** On `give_up` the graph could try a web search before it surrenders.
- **LangChain helpers.** There is a retriever you can use as `search` (lesson 7), and `create_agent` style helpers, but writing the graph yourself shows you what happens (names from memory, check the docs).
- **Evaluation.** Measure answer quality **and** the number of model calls per question. A system that is 2% better and 5 times slower may not be an improvement.

## Common mistakes

- Answering even when no chunk is relevant.
- A rewrite loop with no limit.
- Grading with a big model and paying for it on every chunk.
- Treating "no" from a weak grader as the truth without checking it on examples.
- Forgetting that `tries` must grow, so the router never reaches `give_up`.
- Putting everything into one node, so you cannot see which step failed.
- Never logging the path.

## Interview corner

**What is agentic RAG, and how is it different from plain RAG?**
Plain RAG is a fixed pipeline. Agentic RAG adds decisions: grade the chunks, rewrite the query, retry, choose a source, or refuse. It is a graph with conditional edges and a loop.

**How do you stop an agentic loop from running forever?**
A try counter in the state with a `give_up` exit, plus the framework's recursion limit, plus a cost or time budget.

**Why grade retrieved documents?**
Retrieval always returns something, even junk. Grading removes junk before it reaches the prompt, and it tells you when to retry or refuse.

**What are the costs of agentic RAG?**
More model calls (grading, rewriting), more latency, and more places to fail. Use it where answer quality matters more than speed, and measure it.

**When would you NOT use it?**
When plain RAG already scores well on your eval set, or when latency must be very low. Start simple (lesson 1).

## Summary

- Plain RAG is a line. **Agentic RAG** adds decisions: grade, decide, rewrite, retry, give up.
- A **grader** keeps only clearly relevant chunks (`startswith("yes")`).
- `decide_next` is a plain, testable router: answer, rewrite or give up.
- The loop `rewrite -> retrieve` needs a limit: `max_tries` in the state, and `recursion_limit` as the last wall.
- "I could not find this" is a good answer.
- Stream with `updates` to get the **path**. Log the path and the number of tries.
- Add a decision only if your eval shows it helps.
- Reference: `reference/agentic-langchain-langgraph.md`.
