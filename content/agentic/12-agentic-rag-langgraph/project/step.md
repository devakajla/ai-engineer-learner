# Step 21 — Agentic RAG: check the search, then decide

Plain RAG (step 12) trusts the first search. If the search finds nothing useful, the model either invents an answer or says "I don't know". **Agentic RAG** (agentic lesson 12) adds a **decision**: grade what was found, and if it is poor, **rewrite the question and search again**, with a limit. You build it as a **LangGraph graph**, so every step is a node and the route is visible.

Your folder after this step (new files marked):

```
devdocs-copilot/
├── pyproject.toml      <- adds langgraph
└── copilot/
    ├── agentic_rag.py  <- new
    ├── agentic_cli.py  <- new
    └── ... (all files from step 20)
```

Run `uv sync` after you add `"langgraph>=1.2"` to the dependencies of your `pyproject.toml`.

### 1. `copilot/agentic_rag.py`

```python
"""Agentic RAG as a LangGraph graph: retrieve, grade, then answer, rewrite the question, or give up."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from copilot.embed import embed_texts
from copilot.llm import DEFAULT_MODEL, complete_with_retry
from copilot.rag import NO_ANSWER, build_rag_messages, retrieve


class RagState(TypedDict):
    original: str
    question: str
    hits: list
    relevant: list
    tries: int
    max_tries: int
    answer: str


def grade_hit(client, question, hit, model=DEFAULT_MODEL):
    """Ask the model: does this chunk help to answer the question? True for a clear yes."""
    prompt = (
        "Is this document relevant to the question? Reply yes or no.\n\n"
        f"Question: {question}\n\nDocument: {hit['text']}"
    )
    reply = complete_with_retry(
        client, [{"role": "user", "content": prompt}], model=model, temperature=0, max_completion_tokens=5
    )
    return reply.strip().lower().startswith("yes")


def grade_hits(client, question, hits, model=DEFAULT_MODEL):
    return [hit for hit in hits if grade_hit(client, question, hit, model)]


def decide_next(state):
    """Pure routing: answer when something relevant was found, give up when out of tries, else rewrite."""
    if state["relevant"]:
        return "answer"
    if state["tries"] >= state["max_tries"]:
        return "give_up"
    return "rewrite"


def rewrite_for_search(client, question, model=DEFAULT_MODEL):
    prompt = (
        "Rewrite this question so a search engine finds better results. "
        "Use the words a documentation page would use. Reply with the new question only.\n\n" + question
    )
    text = complete_with_retry(
        client, [{"role": "user", "content": prompt}], model=model, temperature=0, max_completion_tokens=60
    )
    return text.strip() or question


def build_agentic_graph(client, collection, k=3, embed=embed_texts, model=DEFAULT_MODEL):
    """Compile the graph. The nodes use client and collection from this function."""

    def retrieve_node(state):
        hits = retrieve(collection, state["question"], k=k, embed=embed)
        return {"hits": hits, "tries": state["tries"] + 1}

    def grade_node(state):
        return {"relevant": grade_hits(client, state["question"], state["hits"], model)}

    def rewrite_node(state):
        return {"question": rewrite_for_search(client, state["question"], model)}

    def answer_node(state):
        messages = build_rag_messages(state["original"], state["relevant"])
        text = complete_with_retry(client, messages, model=model, temperature=0, max_completion_tokens=300)
        return {"answer": text}

    def give_up_node(state):
        return {"answer": NO_ANSWER}

    graph = StateGraph(RagState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("grade", grade_node)
    graph.add_node("rewrite", rewrite_node)
    graph.add_node("answer", answer_node)
    graph.add_node("give_up", give_up_node)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "grade")
    graph.add_conditional_edges("grade", decide_next, {"answer": "answer", "rewrite": "rewrite", "give_up": "give_up"})
    graph.add_edge("rewrite", "retrieve")
    graph.add_edge("answer", END)
    graph.add_edge("give_up", END)
    return graph.compile()


def agentic_answer(graph, question, max_tries=2):
    """Run the graph. Returns {"answer", "sources", "tries", "path"}.

    path lists the nodes in the order they ran. sources are the ids of the chunks that were used.
    """
    state = {"original": question, "question": question, "hits": [], "relevant": [],
             "tries": 0, "max_tries": max_tries, "answer": ""}
    path = []
    answer = ""
    relevant = []
    for update in graph.stream(state, stream_mode="updates"):
        for node, change in update.items():
            path.append(node)
            if "answer" in change:
                answer = change["answer"]
            if "relevant" in change:
                relevant = change["relevant"]
    sources = [hit["id"] for hit in relevant] if path and path[-1] == "answer" else []
    return {"answer": answer, "sources": sources, "tries": path.count("retrieve"), "path": path}
```

Read it in parts:

1. **`RagState`** is everything the graph remembers: the user's **original** question, the **current** question (it can change), the hits, the relevant hits, the number of searches (`tries`), the limit, and the answer. Nodes return **only the keys they change**.
2. **`grade_hit`** asks a cheap yes/no question per chunk with `temperature=0` and `max_completion_tokens=5`. Only a clear "yes" counts. A grader that says "Yes, because..." still passes, one that rambles about something else does not.
3. **`decide_next`** is plain Python with no model call. Easy to test, and it is the heart of the loop: answer when there is something relevant, give up when out of tries, otherwise rewrite. **The limit lives here.** Without `max_tries` this graph could loop for ever.
4. **`rewrite_for_search`** asks for a version of the question in the words a doc page would use ("remove" becomes "delete"). An empty reply falls back to the old question, so the search never runs on an empty string.
5. **`build_agentic_graph`** wires the five nodes. The nodes are small functions inside it, because they need `client` and `collection` (this is a closure: a function that remembers values from where it was made). The conditional edge after `grade` calls `decide_next` and maps its word to the next node. The edge `rewrite -> retrieve` makes the loop.
6. **The answer uses `state["original"]`**, not the rewritten question. The rewrite is a search trick. The user asked the original question, and the answer should address that.
7. **`give_up_node`** returns `NO_ANSWER` ("I don't know.") with **no** model call. That is the same sentence that the evaluation in step 19 counts as a correct refusal.
8. **`agentic_answer`** runs the graph with `stream_mode="updates"`. Each update names the node that just ran, so you get the `path`, for example `retrieve -> grade -> rewrite -> retrieve -> grade -> answer`. The path is your debug tool and a good test target. `sources` holds the ids of the chunks that were used, and is empty when the graph gave up.

### 2. Run it: `copilot/agentic_cli.py`

```python
"""Ask your docs with the agentic graph. Usage:

    python -m copilot.docs_cli sync docs
    python -m copilot.agentic_cli "how do I remove a task"
"""

import sys

from copilot.agentic_rag import agentic_answer, build_agentic_graph
from copilot.llm import get_client
from copilot.store import open_collection

DB_PATH = ".chroma"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    graph = build_agentic_graph(get_client(), open_collection(DB_PATH))
    result = agentic_answer(graph, " ".join(sys.argv[1:]))
    print("path:", " -> ".join(result["path"]))
    print("searches:", result["tries"])
    print(result["answer"])
    if result["sources"]:
        print("sources:", ", ".join(result["sources"]))


if __name__ == "__main__":
    main()
```

Try a question in your own words, such as `how do I remove a task` when the docs say "delete". Look at the **path** and at **searches**. Then ask something the docs do not cover. The path must end with `give_up`.

> Cost check: every grade is one model call per chunk. Three chunks and two tries can mean 6 grading calls plus a rewrite. That is why the grader is short and uses `max_completion_tokens=5`. Measure it in step 23.

### Checkpoint

Run the tests. Then compare, with your own golden questions, step 12 (plain RAG) and this graph: how many questions got a better answer, and how many extra model calls did it cost? Write both numbers down. "Better" without a cost is not a result.
